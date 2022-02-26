from typing import Iterable

from playcards import Card, Deck52


def _get_card_score(card: Card) -> int:
    """Returns score of one card.
    Ace is treated as 1, not 11
    """
    score = max(Deck52.CARD_RANKS.index(card.rank) + 1, 10)
    return score

def get_hand_score(cards: Iterable[Card]) -> int:
    """Returns score of multiple cards (in hand).
    Aces are treated as to maximize score without getting bust
    """
    score = sum(_get_card_score(card) for card in cards)
    aces_count = sum(1 for card in cards if card.rank == 'A')
    return score + 10 * min((21 - score) // 10, aces_count)

def estimate_hand(cards: Iterable[Card]) -> int:
    """Returns shortage to blackjack:
        negative value for bust,
        zero for blackjack
        and positive value otherwise
    """
    return 21 - get_hand_score(cards)

def is_blackjack(cards: Iterable[Card]) -> bool:
    return get_hand_score(cards) == 21

def is_bust(cards: Iterable[Card]) -> bool:
    return get_hand_score(cards) > 21