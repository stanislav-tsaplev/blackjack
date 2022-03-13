from typing import List

from .playcards import Card, CardRank


class PlayerHand:
    def __init__(self, cards: List[Card]):
        self.cards = cards
        self._pre_score = sum(min(card.rank.value, 10) for card in self.cards)
        self._plus_score = 10 if (
                self._pre_score <= 11 and 
                any(card.rank == CardRank.Ace for card in self.cards)
            ) else 0

    def take(self, card: Card):
        self.cards.append(card)
        self._pre_score += min(card.rank.value, 10)
        self._plus_score = 10 if (
                self._pre_score <= 11 and 
                any(card.rank == CardRank.Ace for card in self.cards)
            ) else 0

    @property
    def score(self) -> int:
        return self._pre_score + self._plus_score

    def is_blackjack(self) -> bool:
        return self.score == 21

    def is_bust(self) -> bool:
        return self.score > 21

    def __str__(self):
        return ' '.join(str(card) for card in self.cards)