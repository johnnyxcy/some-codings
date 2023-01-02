import enum
import dataclasses

import unittest


class Color(enum.Enum):
    RED = 1
    YELLOW = 2
    BLUE = 3
    GREEN = 4
    GOLDEN = 5


@dataclasses.dataclass
class Card:
    cost: dict[Color, int]
    color: Color


@dataclasses.dataclass
class Player:
    wallet: dict[Color, int]
    owned: list[Card] = dataclasses.field(default_factory=list)


class Game:

    def _do_purchase(self, player: Player, card: Card, dry_run: bool,
                     discount: bool) -> bool:
        card_cost = card.cost.copy()
        if discount:
            for owned_card in player.owned:
                if owned_card.color in card_cost.keys():
                    card_cost[owned_card.color] = max(
                        card_cost[owned_card.color] - 1, 0)

        wallet = player.wallet.copy()
        for color, requirement in card_cost.items():
            curr = wallet.get(color, 0)
            if curr < requirement:
                extra_need = requirement - curr
                if wallet.get(Color.GOLDEN, 0) > extra_need:
                    wallet[Color.GOLDEN] -= 1
                else:
                    return False

            if not dry_run:
                wallet[color] -= requirement

        if not dry_run:
            player.wallet = wallet
            player.owned.append(card)

        return True

    def can_purchase(self,
                     player: Player,
                     card: Card,
                     discount: bool = False) -> bool:
        return self._do_purchase(player=player,
                                 card=card,
                                 dry_run=True,
                                 discount=discount)

    def purchase(self,
                 player: Player,
                 card: Card,
                 discount: bool = False) -> bool:
        return self._do_purchase(player=player,
                                 card=card,
                                 dry_run=False,
                                 discount=discount)


class TestGame(unittest.TestCase):
    game: Game

    @classmethod
    def setUpClass(cls) -> None:
        cls.game = Game()

    def test_simple_game(self) -> None:
        player = Player(wallet={
            Color.RED: 10,
            Color.YELLOW: 10,
            Color.BLUE: 10,
            Color.GREEN: 10
        })

        green_card = Card(cost={Color.GREEN: 1}, color=Color.GREEN)

        # can_purchase does not affect player
        self.assertTrue(self.game.can_purchase(player=player, card=green_card))
        self.assertEqual(len(player.owned), 0)
        self.assertListEqual(player.owned, [])

        # purchase do
        self.game.purchase(player=player, card=green_card)
        self.assertEqual(len(player.owned), 1)
        self.assertListEqual(player.owned, [green_card])

    def test_simple_game_with_multiple_purchase(self) -> None:
        player = Player(wallet={
            Color.RED: 11,
            Color.YELLOW: 11,
            Color.BLUE: 11,
            Color.GREEN: 11
        })

        red_card = Card(cost={Color.RED: 3}, color=Color.RED)
        yellow_card = Card(cost={Color.YELLOW: 4}, color=Color.YELLOW)
        blue_card = Card(cost={Color.BLUE: 5}, color=Color.BLUE)
        green_card = Card(cost={Color.GREEN: 6}, color=Color.GREEN)

        self.assertTrue(self.game.can_purchase(player=player, card=red_card))
        self.assertTrue(self.game.can_purchase(player=player,
                                               card=yellow_card))
        self.assertTrue(self.game.can_purchase(player=player, card=blue_card))
        self.assertTrue(self.game.can_purchase(player=player, card=green_card))

        self.game.purchase(player=player, card=red_card)
        self.game.purchase(player=player, card=yellow_card)
        self.game.purchase(player=player, card=blue_card)
        self.game.purchase(player=player, card=green_card)
        self.assertEqual(len(player.owned), 4)
        # order matters
        self.assertListEqual(player.owned,
                             [red_card, yellow_card, blue_card, green_card])

        self.assertTrue(self.game.can_purchase(player=player, card=red_card))
        self.assertTrue(self.game.can_purchase(player=player,
                                               card=yellow_card))
        self.assertTrue(self.game.can_purchase(player=player, card=blue_card))
        # !IMPORTANT
        # since a green card cost 6 green color
        # after paid for one green card
        # player will not have enough currency
        # to pay for another, so can_purchase should
        # return false
        # do the math 11 - 6 = 5 < 6
        self.assertFalse(self.game.can_purchase(player=player,
                                                card=green_card))

    def test_simple_game_with_discount(self) -> None:
        player = Player(wallet={Color.GREEN: 11})

        green_card = Card(cost={Color.GREEN: 6}, color=Color.GREEN)

        self.assertTrue(self.game.can_purchase(player=player, card=green_card))

        self.game.purchase(player=player, card=green_card)
        self.assertEqual(len(player.owned), 1)
        # !IMPORTANT
        # but this time, we have it discounted
        # which means all green card will cost
        # k less where k means the number of
        # green cards owned by player (in this case 1)
        # so now we will have enough currency
        # do the math 11 - 6 = 5 >= 6 - 1 = 4
        self.assertTrue(
            self.game.can_purchase(player=player,
                                   card=green_card,
                                   discount=True))


if __name__ == "__main__":
    unittest.main()
