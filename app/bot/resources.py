import json


BOT_MESSAGES = {
    "player_info.money": "У вас в кошельке:",
    "player_info.hand": "У вас на руке:",
    "player_info.out_of_game": "⏻ Эта информация доступна только в ходе игры",
    
    "game.already_started": "⏻ Игра уже идет. Чтобы начать новую игру, завершите текущую",
    "game.start": "⏻ Игра начата",
    "game.players_list_header": "⏻ Приглашаются:",
    "game.player": "⏿ [{first_name} {last_name}]",
    "game.exit": "Вы вышли из игры",
    "game.end": "⏻ Игра окончена. Всем спасибо за участие",
    "game.terminated": "⏻ Игра прервана досрочно",
    
    "bet.started": "⏻ Делайте ваши ставки, господа!",
    "bet.request": "Делайте вашу ставку:",
    "bet.accepted": "Ставка принята",
    "bet.rejected": "Ставка отклонена. У вас недостаточно денег",
    "bet.discarded": "К сожалению, вы не участвуете в игре",
    "bet.completed": "⏻ Ставки сделаны. Начинаем игру",
    
    "deal.initial": "Ваши карты:",
    "deal.started": "⏻ Начинаю раздачу карт",
    "deal.new_card": "Ваша карта:",
    "deal.hand": "У вас на руке:",
    "deal.bust": "Перебор!",
    "deal.blackjack": "Блэкджек!",
    "deal.next": "⏻ Перехожу к следующему игроку",
    "deal.completed": "⏻ Все карты розданы",

    "hit_or_stand.request": "Хватит или ещё?",
    "hit_or_stand.hit_button_label": "Ещё",
    "hit_or_stand.stand_button_label": "Хватит",
    "hit_or_stand.stand_accepted": "Вас понял, карты больше не сдаю. Подождите конца игры",
    
    "dealer.start": "⏻ Сдаю себе",
    "dealer.initial": "⁂ У меня:",
    "dealer.hit": "⁂ Беру еще",
    "dealer.new_card": "⁂ Моя карта:",
    "dealer.hand": "⁂ У меня на руке:",
    "dealer.bust": "⁂ Перебор!",
    "dealer.blackjack": "⁂ Блэкджек!",
    "dealer.stand": "⁂ Хватит",
    
    "payout.start": "⏻ Итоги игры:",
    "payout.dealer_bust": "У дилера перебор. Ваш выигрыш: {gain}",
    "payout.player_bust": "У вас перебор. Вы проиграли",
    "payout.player_win": "У вас больше очков, чем у дилера. Ваш выигрыш: {gain}",
    "payout.player_tie": "Вы сыграли с дилером вничью. Ваш выигрыш: {gain}",
    "payout.player_lose": "У вас меньше очков, чем у дилера. Вы проиграли",
}

BOT_KEYBOARDS = {
    "empty": json.dumps(
        {
            "one_time": True,
            "buttons": []
        }
    ),
    "hit_or_stand": json.dumps(
        {
            "one_time": False,
            "buttons": [
                [  
                    {  
                        "action": {  
                            "type": "text",
                            "payload": json.dumps("hit"),
                            "label": BOT_MESSAGES["hit_or_stand.hit_button_label"]
                        },
                        "color": "primary"
                    },
                    {  
                        "action": {  
                            "type": "text",
                            "payload": json.dumps("stand"),
                            "label": BOT_MESSAGES["hit_or_stand.stand_button_label"]
                        },
                        "color": "primary"
                    }
                ]
            ]
        }
    )
}