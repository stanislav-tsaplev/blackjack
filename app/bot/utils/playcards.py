from dataclasses import dataclass
from random import shuffle, choice


@dataclass
class Card:
    suit: str
    rank: str

    def __str__(self):
        return self.rank + self.suit
    
    def __repr__(self):
        return self.rank + self.suit


class Deck36:
    CARD_SUITS = '♣♦♥♠'
    CARD_RANKS = '6789⑩JQKA'
    # CARD_RANKS = '⑥⑦⑧⑨⑩JQKA'

class Deck52:
    CARD_SUITS = '♣♦♥♠'
    CARD_RANKS = 'A23456789⑩JQK'
    # CARD_RANKS = 'A②③④⑤⑥⑦⑧⑨⑩JQK'
    

def get_random_card(deck=Deck52) -> Card:
    return Card(
        suit=choice(deck.CARD_SUITS), 
        rank=choice(deck.CARD_RANKS)
    )

def get_ordered_deck(deck=Deck52) -> list[Card]:
    return [Card(suit, rank) 
            for suit in deck.CARD_SUITS 
            for rank in deck.CARD_RANKS]

def get_shuffled_deck(deck=Deck52) -> list[Card]:
    deck = [Card(suit, rank) 
            for suit in deck.CARD_SUITS 
            for rank in deck.CARD_RANKS]
    shuffle(deck)
    return deck
