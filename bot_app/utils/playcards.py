from dataclasses import dataclass
from random import shuffle, choice

from common.db.gino_models.card_deal import CardSuit, CardRank


CARD_SUIT_CHARS = ' ♣♦♥♠'
# CARD_RANK_CHARS = ' A23456789⑽JQK'
CARD_RANK_CHARS = ' A23456789㉈JQK'

@dataclass
class Card:
    suit: CardSuit
    rank: CardRank

    def __str__(self):
        return CARD_RANK_CHARS[self.rank.value] + \
                CARD_SUIT_CHARS[self.suit.value]


deck = [Card(suit, rank) 
        for suit in CardSuit 
        for rank in CardRank]

def get_random_card() -> Card:
    return choice(deck)

def get_ordered_deck() -> list[Card]:
    return [Card(suit, rank) 
            for suit in CardSuit 
            for rank in CardRank]

def get_shuffled_deck() -> list[Card]:
    deck = [Card(suit, rank) 
            for suit in CardSuit 
            for rank in CardRank]
    shuffle(deck)
    return deck
