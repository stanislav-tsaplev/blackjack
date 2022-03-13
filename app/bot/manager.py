from typing import (
    Optional, Union, Callable, Coroutine, Mapping, 
    TYPE_CHECKING
)
from logging import getLogger
from string import Template

import asyncio

from app.vk_api.models import *
from app.vk_api.utils import is_sent_from_chat
from app.db.game.models import *
from app.bot.data_extractors import *
from app.bot.utils.playcards import *
from app.bot.utils.player_hand import *
from app.bot.resources import BOT_MESSAGES, BOT_KEYBOARDS

if TYPE_CHECKING:
    from app.web.app import Application


COMMAND_PREFIX = '!'

TIME_TO_WAIT_PLAYER_RESPONSE = 30   # sec
DB_POLLING_FREQUENCY = 5            # sec

PLAYERS_TOP = 3

class BotManager:
    def __init__(self, app: "Application"):
        self.logger = getLogger(self.__class__.__name__)
        self.app = app

        self.data_extractors: Mapping[str, Callable[ [str], Union[str, list, dict] ]] = {
            "bet_data_extractor": bet_data_extractor,
            "hit_or_stand_data_extractor": hit_or_stand_data_extractor,
        }
        self.command_handlers: Mapping[str, Coroutine[int, int, None]] = {
            "game": self.launch_game,
            "игра": self.launch_game,
            "hand": self.show_player_hand,
            "рука": self.show_player_hand,
            "money": self.show_player_money,
            "сумма": self.show_player_money,
            "top": self.show_players_top,
            "топ": self.show_players_top,
            "quit": self.cut_out_player,
            "exit": self.cut_out_player,
            "выход": self.cut_out_player,
            "stop": self.terminate_game,
            "стоп": self.terminate_game,
        }

    async def restore_opened_games(self, *args, **kwargs):
        opened_game_sessions = await self.app.db_store.game_sessions \
                                                .get_all_opened_game_sessions()
        for game_session in opened_game_sessions:
            asyncio.create_task(self.restore_game(game_session))

    def get_vk_countdown_callback(self,
        chat_id: int,
        updating_message_id: int, 
        updating_message_text_template: Template
    ) -> Callable[[Optional[int]], None]:
        async def vk_countdown(countdown: Optional[int]) -> None:
            countdown_indicator = ""
            # countdown == None and countdown == 0 are treated differently
            # the latter means time was over 
            # while the former means choice was made
            if countdown is not None:   
                countdown_indicator = ( # ⏳⏱
                    f"⏱{countdown} "
                    f"{'||' * (countdown // DB_POLLING_FREQUENCY)}"
                )

            await self.app.vk_api.update_message(
                chat_id, 
                updating_message_id,
                updating_message_text_template.substitute(
                    countdown=countdown_indicator
                )
            )
        return vk_countdown

    async def get_deferred_player_response(self, user_id: int, chat_id: int,
            countdown_callback: Callable[[Optional[int]], None]) -> Union[str, list, dict]:
        async def _get_deferred_player_response():
            countdown = TIME_TO_WAIT_PLAYER_RESPONSE
            await countdown_callback(countdown)

            response_data = None
            while response_data is None and countdown > 0:
                await asyncio.sleep(DB_POLLING_FREQUENCY)
                countdown -= DB_POLLING_FREQUENCY
                await countdown_callback(countdown)
                
                response_data = await self.app.db_store.player_dataports \
                                        .get_player_response_data(user_id, chat_id)

            if countdown > 0:
                await countdown_callback(None)
            return response_data

        player_response_task = asyncio.create_task(
            _get_deferred_player_response()
        )
        
        await player_response_task
        return player_response_task.result()

    async def restore_game(self, game_session: GameSession):
        game_phases = [
            self.betting,       # for GameSessionState.OPENED
            self.betting,
            self.initial_deal,
            self.dealing,
            self.dealer_game,
            self.paying_out,
            self.end_game
        ]

        await self.app.vk_api.send_message(game_session.chat_id, 
                                        BOT_MESSAGES["game.restored"])
        for game_phase in game_phases[game_session.state.value: ]:
            await game_phase(game_session)

    async def launch_game(self, chat_id: int, user_id: int):
        if await self.check_for_already_launched_game(chat_id):
            return

        game_session = await self.start_game(chat_id)
        
        await self.betting(game_session)
        await self.initial_deal(game_session)
        await self.dealing(game_session)
        await self.dealer_game(game_session)
        await self.paying_out(game_session)
        await self.end_game(game_session)

    async def check_for_already_launched_game(self, chat_id: int) -> bool:
        current_game_session_exists = await self.app.db_store.game_sessions \
                                        .has_current_game_session(chat_id)
        if current_game_session_exists:
            await self.app.vk_api.send_message(chat_id, 
                                        BOT_MESSAGES["game.already_started"])
        return current_game_session_exists

    async def start_game(self, chat_id: int) -> GameSession:
        active_member_profiles = \
            await self.app.vk_api.get_active_member_profiles(chat_id)
            
        user_profiles = [
            UserProfile(
                vk_id=member_profile.id,
                first_name=member_profile.first_name,
                last_name=member_profile.last_name
            ) for member_profile in active_member_profiles
        ]
        game_session = await self.app.db_store.game_sessions \
                                        .create_game_session(chat_id, user_profiles)
        
        await self.app.vk_api.send_message(chat_id, BOT_MESSAGES["game.start"])
        await self.app.vk_api.send_message(chat_id,
                                        BOT_MESSAGES["game.players_list_header"])
        
        await self.app.vk_api.send_message(
            chat_id, 
            "<br>".join(
                BOT_MESSAGES["game.player"].format(
                    first_name=player_session.player.user_profile.first_name,
                    last_name=player_session.player.user_profile.last_name
                )
                for player_session in game_session.player_sessions
            )
        )
        return game_session

    async def betting(self, game_session: GameSession):
        await self.app.db_store.game_sessions.set_game_session_state(
                                                game_session, 
                                                GameSessionState.BETTING)
        await self.app.vk_api.send_message(game_session.chat_id, BOT_MESSAGES["bet.started"])
        for player_session in game_session.player_sessions:
            if player_session.state != PlayerSessionState.BETTING:
                break

            user_profile = player_session.player.user_profile
            await self.app.db_store.player_dataports.put_player_request_data(
                                                        user_id=user_profile.vk_id,
                                                        chat_id=game_session.chat_id, 
                                                        request_data={
                                                            "data_extractor": 
                                                                "bet_data_extractor"
                                                        })

            bet_request_text_template = Template(
                f'{BOT_MESSAGES["game.player"]} '
                f'{BOT_MESSAGES["bet.request"]} '
                f'$countdown'.format(
                    first_name=user_profile.first_name,
                    last_name=user_profile.last_name)
            )
            bet_request_message_id = await self.app.vk_api \
                .send_message(game_session.chat_id, bet_request_text_template \
                                                    .substitute(countdown=""))

            bet_request_countdown_callback = self.get_vk_countdown_callback(
                                                        game_session.chat_id,
                                                        bet_request_message_id, 
                                                        bet_request_text_template)
            player_response = await self.get_deferred_player_response(
                                                        user_id=user_profile.vk_id,
                                                        chat_id=game_session.chat_id, 
                                                        countdown_callback=
                                                            bet_request_countdown_callback)

            if player_response is not None:
                bet = player_response["bet"]
                success = await self.app.db_store.player_sessions.take_player_bet(
                                                                player_session, bet=bet)
                if success:
                    await self.app.vk_api.send_message(game_session.chat_id,
                                                f'{BOT_MESSAGES["game.player"]} '
                                                f'{BOT_MESSAGES["bet.accepted"]}'.format(
                                                    first_name=user_profile.first_name,
                                                    last_name=user_profile.last_name))
                else:
                    await self.app.db_store.player_sessions.cut_out_player(player_session)
                    await self.app.vk_api.send_message(game_session.chat_id,
                                                f'{BOT_MESSAGES["game.player"]} '
                                                f'{BOT_MESSAGES["bet.rejected"]}'.format(
                                                    first_name=user_profile.first_name,
                                                    last_name=user_profile.last_name))
            else:
                await self.app.db_store.player_sessions.cut_out_player(player_session)
                await self.app.vk_api.send_message(game_session.chat_id,
                                                f'{BOT_MESSAGES["game.player"]} '
                                                f'{BOT_MESSAGES["bet.discarded"]}'.format(
                                                    first_name=user_profile.first_name,
                                                    last_name=user_profile.last_name))
            await self.app.db_store.player_dataports.clear_player_dataport(
                                                        user_id=user_profile.vk_id,
                                                        chat_id=game_session.chat_id)
        await self.app.vk_api.send_message(game_session.chat_id,
                                                BOT_MESSAGES["bet.completed"])

    async def initial_deal(self, game_session: GameSession):
        await self.app.db_store.game_sessions.set_game_session_state(
                                                game_session, 
                                                GameSessionState.INITIAL_DEAL)
        dealing_players = await self.app.db_store.player_sessions \
                                            .get_dealing_players(game_session)
        
        for player_session in dealing_players:
            if player_session.state != PlayerSessionState.INITIAL_DEAL:
                break

            card1 = get_random_card()
            card2 = get_random_card()
            await self.app.db_store.card_deals.add_initial_cards(player_session, 
                                                            cards=(card1, card2))
            user_profile = player_session.player.user_profile
            await self.app.vk_api.send_message(game_session.chat_id,
                                                f'{BOT_MESSAGES["game.player"]} '
                                                f'{BOT_MESSAGES["deal.initial.player"]} '
                                                f'{card1} {card2}'.format(
                                                    first_name=user_profile.first_name,
                                                    last_name=user_profile.last_name))
            hand = PlayerHand((card1, card2))
            if hand.is_blackjack():
                await self.app.db_store.player_sessions \
                                        .break_out_player(
                                            player_session,
                                            breakout_reason="blackjack")
                await self.app.vk_api.send_message(game_session.chat_id,
                                f'{BOT_MESSAGES["game.player"]} '
                                f'{BOT_MESSAGES["deal.blackjack"]}'.format(
                                    first_name=user_profile.first_name,
                                    last_name=user_profile.last_name
                                )
                )
            
        card1 = get_random_card()
        card2 = get_random_card()
        await self.app.db_store.card_deals.add_initial_cards(game_session.dealer_session, 
                                                                    cards=(card1, card2))
        await self.app.vk_api.send_message(game_session.chat_id,
                                            f'{BOT_MESSAGES["deal.initial.dealer"]} '
                                            f'{card1} '
                                            f'{BOT_MESSAGES["deal.hidden_card"]}')
        

    async def dealing(self, game_session: GameSession):
        await self.app.db_store.game_sessions.set_game_session_state(
                                                game_session, 
                                                GameSessionState.DEALING)
        await self.app.vk_api.send_message_with_keyboard(game_session.chat_id,
                                            BOT_MESSAGES["deal.started"],
                                            BOT_KEYBOARDS["hit_or_stand"])
        while True:
            dealing_players = await self.app.db_store.player_sessions \
                                            .get_dealing_players(game_session)
            if not dealing_players:
                break

            for player_session in dealing_players:
                user_profile = player_session.player.user_profile
                await self.app.db_store.player_dataports.put_player_request_data(
                                        user_id=user_profile.vk_id,
                                        chat_id=game_session.chat_id, 
                                        request_data={
                                            "data_extractor": "hit_or_stand_data_extractor"
                                        })

                hand = await self.app.db_store.card_deals.get_player_hand(player_session)                
                await self.app.vk_api.send_message(game_session.chat_id,
                                                f'{BOT_MESSAGES["game.player"]} '
                                                f'{BOT_MESSAGES["deal.hand"]} '
                                                f'{hand}'.format(
                                                    first_name=user_profile.first_name,
                                                    last_name=user_profile.last_name)
                                                )                                   

                hit_or_stand_request_text_template = Template(
                    f'{BOT_MESSAGES["game.player"]} '
                    f'{BOT_MESSAGES["hit_or_stand.request"]} '
                    f'$countdown'.format(
                        first_name=user_profile.first_name,
                        last_name=user_profile.last_name)
                )
                hit_or_stand_request_message_id = await self.app.vk_api.send_message(
                    game_session.chat_id, 
                    hit_or_stand_request_text_template.substitute(countdown=""))

                hit_or_stand_request_countdown_callback = self.get_vk_countdown_callback(
                    game_session.chat_id,
                    hit_or_stand_request_message_id, 
                    hit_or_stand_request_text_template)

                player_response = await self.get_deferred_player_response(
                                user_id=user_profile.vk_id,
                                chat_id=game_session.chat_id,
                                countdown_callback=hit_or_stand_request_countdown_callback)
                if player_response is not None:
                    choice = player_response["choice"]
                    if choice == "hit":
                        card = get_random_card()
                        hand.take(card)

                        await self.app.db_store.card_deals.add_card(player_session, card)
                        await self.app.vk_api.send_message(game_session.chat_id,
                                                f'{BOT_MESSAGES["game.player"]} '
                                                f'{BOT_MESSAGES["deal.new_card"]} '
                                                f'{card}'.format(
                                                    first_name=user_profile.first_name,
                                                    last_name=user_profile.last_name)
                                                )

                        if hand.is_bust():
                            await self.app.db_store.player_sessions \
                                                    .break_out_player(
                                                        player_session,
                                                        breakout_reason="bust")
                            await self.app.vk_api.send_message(game_session.chat_id,
                                                f'{BOT_MESSAGES["game.player"]} '
                                                f'{BOT_MESSAGES["deal.bust"]}'.format(
                                                    first_name=user_profile.first_name,
                                                    last_name=user_profile.last_name)
                                                )

                        elif hand.is_blackjack():
                            await self.app.db_store.player_sessions \
                                                    .break_out_player(
                                                        player_session,
                                                        breakout_reason="blackjack")
                            await self.app.vk_api.send_message(game_session.chat_id,
                                            f'{BOT_MESSAGES["game.player"]} '
                                            f'{BOT_MESSAGES["deal.blackjack"]}'.format(
                                                first_name=user_profile.first_name,
                                                last_name=user_profile.last_name)
                                            )

                    else:   # choice == "stand"
                        await self.app.db_store.player_sessions \
                                                    .break_out_player(
                                                        player_session,
                                                        breakout_reason="stand")
                        await self.app.vk_api.send_message(game_session.chat_id,
                                f'{BOT_MESSAGES["game.player"]} '
                                f'{BOT_MESSAGES["hit_or_stand.stand_accepted"]}'.format(
                                    first_name=user_profile.first_name,
                                    last_name=user_profile.last_name)
                                )
                # if player missed the time, 
                # we treat them as if they choosed to stand
                else:
                    await self.app.db_store.player_sessions \
                                                    .break_out_player(
                                                        player_session,
                                                        breakout_reason="stand")
                    await self.app.vk_api.send_message(game_session.chat_id,
                                f'{BOT_MESSAGES["game.player"]} '
                                f'{BOT_MESSAGES["hit_or_stand.stand_accepted"]}'.format(
                                    first_name=user_profile.first_name,
                                    last_name=user_profile.last_name))

                await self.app.db_store.player_dataports \
                                            .clear_player_dataport(
                                                user_id=user_profile.vk_id,
                                                chat_id=game_session.chat_id)
                await self.app.db_store.player_sessions.update_timestamp(player_session)
                await self.app.vk_api.send_message(game_session.chat_id,
                                            BOT_MESSAGES["deal.next"])
        
        await self.app.vk_api.send_message_with_keyboard(game_session.chat_id,
                                                BOT_MESSAGES["deal.completed"],
                                                BOT_KEYBOARDS["empty"])

    async def dealer_game(self, game_session: GameSession):
        await self.app.db_store.game_sessions.set_game_session_state(
                                                game_session, 
                                                GameSessionState.DEALER_GAME)
        await self.app.vk_api.send_message(game_session.chat_id, BOT_MESSAGES["dealer.start"])
        await asyncio.sleep(2)

        dealer_session = game_session.dealer_session
        dealer_hand = await self.app.db_store.card_deals.get_player_hand(dealer_session)
        await self.app.vk_api.send_message(game_session.chat_id,
                                            f'{BOT_MESSAGES["dealer.initial"]} '
                                            f'{dealer_hand}')
        await asyncio.sleep(1)

        if dealer_hand.is_blackjack():
            await self.app.vk_api.send_message(game_session.chat_id,
                                                f'{BOT_MESSAGES["dealer.hand"]} '
                                                f'{dealer_hand}')
            await self.app.vk_api.send_message(game_session.chat_id,
                                                    BOT_MESSAGES["dealer.blackjack"])

        while dealer_hand.score < 17:
            await self.app.vk_api.send_message(game_session.chat_id, 
                                                        BOT_MESSAGES["dealer.hit"])
            await asyncio.sleep(2)

            card = get_random_card()
            dealer_hand.take(card)
            await self.app.db_store.card_deals.add_card(dealer_session, card)
            await self.app.vk_api.send_message(game_session.chat_id,
                                            f'{BOT_MESSAGES["dealer.new_card"]} {card}')
            await asyncio.sleep(1)
            
            if dealer_hand.is_bust():
                await self.app.vk_api.send_message(game_session.chat_id,
                                                    f'{BOT_MESSAGES["dealer.hand"]} '
                                                    f'{dealer_hand}')
                await self.app.vk_api.send_message(game_session.chat_id,
                                                        BOT_MESSAGES["dealer.bust"])
                break
            if dealer_hand.is_blackjack():
                await self.app.vk_api.send_message(game_session.chat_id,
                                                    f'{BOT_MESSAGES["dealer.hand"]} '
                                                    f'{dealer_hand}')
                await self.app.vk_api.send_message(game_session.chat_id,
                                                        BOT_MESSAGES["dealer.blackjack"])
                break
        else:
            await self.app.vk_api.send_message(game_session.chat_id,
                                                        BOT_MESSAGES["dealer.stand"])
            await self.app.vk_api.send_message(game_session.chat_id,
                                                    f'{BOT_MESSAGES["dealer.hand"]} '
                                                    f'{dealer_hand}')
        await asyncio.sleep(2)

    async def paying_out(self, game_session: GameSession):
        await self.app.db_store.game_sessions.set_game_session_state(
                                                game_session, 
                                                GameSessionState.PAYING_OUT)
        dealer_session = game_session.dealer_session
        dealer_hand = await self.app.db_store.card_deals \
                                            .get_player_hand(dealer_session)

        await self.app.vk_api.send_message(game_session.chat_id,
                                                        BOT_MESSAGES["payout.start"])
        broken_out_players = await self.app.db_store.player_sessions \
                                                    .get_broken_out_players(game_session)
        for player_session in broken_out_players:
            user_profile = player_session.player.user_profile

            if player_session.state == PlayerSessionState.BUSTED:
                await self.app.vk_api.send_message(game_session.chat_id,
                                        f'{BOT_MESSAGES["game.player"]} '
                                        f'{BOT_MESSAGES["payout.player_bust"]}'.format(
                                            first_name=user_profile.first_name,
                                            last_name=user_profile.last_name))
                player_payout_ratio = 0
            elif dealer_hand.is_bust():
                await self.app.vk_api.send_message(game_session.chat_id,
                                        f'{BOT_MESSAGES["game.player"]} '
                                        f'{BOT_MESSAGES["payout.dealer_bust"]}'.format(
                                            first_name=user_profile.first_name,
                                            last_name=user_profile.last_name,
                                            gain=player_session.bet * 2))
                player_payout_ratio = 2
            else:
                player_hand = await self.app.db_store.card_deals \
                                                    .get_player_hand(player_session)
                score_diff = player_hand.score - dealer_hand.score
                if score_diff > 0:
                    await self.app.vk_api.send_message(game_session.chat_id,
                                            f'{BOT_MESSAGES["game.player"]} '
                                            f'{BOT_MESSAGES["payout.player_win"]}'.format(
                                                first_name=user_profile.first_name,
                                                last_name=user_profile.last_name,
                                                gain=player_session.bet * 2))
                    player_payout_ratio = 2
                elif score_diff == 0:
                    await self.app.vk_api.send_message(game_session.chat_id,
                                            f'{BOT_MESSAGES["game.player"]} '
                                            f'{BOT_MESSAGES["payout.player_tie"]}'.format(
                                                first_name=user_profile.first_name,
                                                last_name=user_profile.last_name,
                                                gain=player_session.bet)
                                            )
                    player_payout_ratio = 1
                else:   # score_diff < 0
                    await self.app.vk_api.send_message(game_session.chat_id,
                                            f'{BOT_MESSAGES["game.player"]} '
                                            f'{BOT_MESSAGES["payout.player_lose"]}'.format(
                                                first_name=user_profile.first_name,
                                                last_name=user_profile.last_name))
                    player_payout_ratio = 0

            await self.app.db_store.player_sessions \
                                    .pay_out_player(player_session, player_payout_ratio)

    async def end_game(self, game_session: GameSession):
        await self.app.db_store.game_sessions.close_game_session(game_session)
        await self.app.vk_api.send_message(game_session.chat_id, BOT_MESSAGES["game.end"])

    async def show_player_hand(self, chat_id: int, user_id: int):
        player_session = await self.app.db_store.player_sessions \
                                    .get_current_player_session(user_id, chat_id)
        if player_session is None:
            await self.app.vk_api.send_message(chat_id, BOT_MESSAGES["player_info.out_of_game"])
            return

        user_profile = player_session.player.user_profile
        hand = await self.app.db_store.card_deals.get_player_hand(player_session)
        await self.app.vk_api.send_message(chat_id,
                                f'{BOT_MESSAGES["game.player"]} '
                                f'{BOT_MESSAGES["player_info.hand"]} '
                                f'{hand}'.format(
                                    first_name=user_profile.first_name,
                                    last_name=user_profile.last_name))

    async def show_player_money(self, chat_id: int, user_id: int):
        player = await self.app.db_store.players.get_player(user_id, chat_id)
        if player is None:
            return
                       
        await self.app.vk_api.send_message(chat_id,
                                f'{BOT_MESSAGES["game.player"]} '
                                f'{BOT_MESSAGES["player_info.money"]} '
                                f'{player.money}'.format(
                                    first_name=player.user_profile.first_name,
                                    last_name=player.user_profile.last_name))

    async def show_players_top(self, chat_id: int, user_id: int):
        players_top = await self.app.db_store.players \
                                .get_successful_players_list(PLAYERS_TOP)
        await self.app.vk_api.send_message(
            chat_id, 
            BOT_MESSAGES["player_info.top_header"]
        )                                             
        await self.app.vk_api.send_message(
            chat_id, 
            "<br>".join(
                BOT_MESSAGES["player_info.top_item"].format(
                    first_name=player.user_profile.first_name,
                    last_name=player.user_profile.last_name,
                    chat_name=player.game_chat.name,
                    money=player.money
                )
                for player in players_top
            )
        )

    async def cut_out_player(self, chat_id: int, user_id: int):
        player_session = await self.app.db_store.player_sessions \
                                    .get_current_player_session(user_id, chat_id)
        if player_session is None:
            return

        user_profile = player_session.player.user_profile
        await self.app.db_store.player_sessions.cut_out_player(player_session)
        await self.app.vk_api.send_message(chat_id,
                                f'{BOT_MESSAGES["game.player"]} '
                                f'{BOT_MESSAGES["game.exit"]}'.format(
                                    first_name=user_profile.first_name,
                                    last_name=user_profile.last_name))

    async def terminate_game(self, chat_id: int, user_id: int):
        game_session = await self.app.db_store.game_sessions \
                                        .get_current_game_session(chat_id)
        await self.app.db_store.game_sessions.terminate_game_session(game_session)
        await self.app.vk_api.send_message_with_keyboard(game_session.chat_id, 
                                                BOT_MESSAGES["game.terminated"],
                                                BOT_KEYBOARDS["empty"])
        for task in asyncio.all_tasks():
            if task.get_name() == str(chat_id):
                task.cancel()

    async def handle_command(self, message: VkApiMessage):
        command = message.text.removeprefix(COMMAND_PREFIX).strip()
        command_handler = self.command_handlers.get(command)
        if command_handler is not None:
            asyncio.create_task(
                command_handler(
                    chat_id=message.peer_id, 
                    user_id=message.from_id),
                name=message.peer_id    # NOT unique for different commands in one chat
            )

    async def handle_new_message(self, message: VkApiMessage):
        player_request_data = await self.app.db_store.player_dataports \
                                                    .get_player_request_data(
                                                        user_id=message.from_id,
                                                        chat_id=message.peer_id)

        if player_request_data is None:
            # self.logger.info(f"unexcepted message from player: {message}")
            return

        data_extractor = self.data_extractors.get(player_request_data["data_extractor"])
        if data_extractor is None:
            self.logger.error(f"data extractor for {player_request_data} is not found")
            return
        
        try:
            text = message.text if message.payload is None else message.payload            
            response_data = data_extractor(text)
            await self.app.db_store.player_dataports.put_player_response_data(
                                                        user_id=message.from_id,
                                                        chat_id=message.peer_id, 
                                                        response_data=response_data)
        except ValueError as e:
            self.logger.warning(
                f"message received from player: '{message}' is inappropriate "
                f"for player request: {player_request_data}; will be ignored",
                exc_info=e
            )

    async def handle_updates(self, updates: list[VkApiUpdate]):
        for update in updates:
            if update.type == "message_new":
                vk_api_message = update.object.message
                if is_sent_from_chat(vk_api_message):
                    if vk_api_message.text.startswith(COMMAND_PREFIX):
                        await self.handle_command(vk_api_message)
                    else:
                            await self.handle_new_message(vk_api_message)
