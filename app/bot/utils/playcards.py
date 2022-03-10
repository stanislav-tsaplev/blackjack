from typing import List
from dataclasses import dataclass
from enum import IntEnum
from random import shuffle, choice


class CardRank(IntEnum):
    Ace = 1
    Two = 2
    Three = 3
    Four = 4
    Five = 5
    Six = 6
    Seven = 7
    Eight = 8
    Nine = 9
    Ten = 10
    Jack = 11
    Queen = 12
    King = 13

class CardSuit(IntEnum):
    Clubs = 1
    Diamonds = 2
    Hearts = 3
    Spades = 4


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
