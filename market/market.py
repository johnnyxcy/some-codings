from __future__ import annotations

import typing
import dataclasses
import enum
import abc
from datetime import datetime


class OrderType(enum.IntEnum):
    ORDER_TYPE_SELL = 0
    ORDER_TYPE_BUY = 1


@dataclasses.dataclass
class IUser(abc.ABC):

    uid: str

    meta: typing.Any
    """Any metadata you could extend your user"""

    @abc.abstractmethod
    def buy(self, price: float) -> None:
        """you could extend the return type to be an order type or an Promise of order type
        to get the real order with buy api
        """
        pass

    @abc.abstractmethod
    def sell(self, price: float) -> None:
        """sell buy"""
        pass


@dataclasses.dataclass
class Order(object):
    price: float

    order_type: OrderType

    user: IUser
    """Any user could make a sell or buy order
    
    you could make further validations based on this property

    e.g.:
        1. An order could not be consumed by the user who produced it
    """

    order_time: datetime
    """you could extend your program with the use of order time
    
    such as:
        1. if two orders with price, use the newest one instead of older ones
        2. some bid game
    """


T = typing.TypeVar("T")


def insertion_sort(container: list[T], el: T, key_comparison: typing.Callable[[T], typing.Any]) -> None:
    # TODO: do your insertion sort algorithm here
    # put el into container
    pass

    container.append(el)
    container.sort(key=key_comparison)


class Market(object):

    def __init__(self) -> None:
        # all orders are sorted from lowest price to highest price
        # !actually a double-headed linked list is better here but anyway
        self.buy_orders: list[Order] = []
        self.sell_orders: list[Order] = []

    def transaction(self, incoming_order: Order) -> None:
        desired_price = incoming_order.price
        if incoming_order.order_type == OrderType.ORDER_TYPE_BUY:
            # if is a buy order, user is expecting cheapest sell order
            if len(self.sell_orders) > 0 and desired_price >= self.sell_orders[0].price:
                # cheers, you made a deal
                self.sell_orders.pop(0)
            else:
                insertion_sort(self.buy_orders, incoming_order, lambda o: o.price)

        elif incoming_order.order_type == OrderType.ORDER_TYPE_SELL:
            # if is a sell order, user is expected highest paid buyer
            if len(self.buy_orders) > 0 and desired_price <= self.buy_orders[len(self.buy_orders) - 1].price:
                # cheers,  you made a deal
                self.buy_orders.pop(-1)
            else:
                insertion_sort(self.sell_orders, incoming_order, lambda o: o.price)


@dataclasses.dataclass
class User(IUser):

    market: Market

    def buy(self, price: float) -> None:
        """you could extend the return type to be an order type or an Promise of order type
        to get the real order with buy api
        """
        self.market.transaction(
            incoming_order=Order(
                price=price, order_type=OrderType.ORDER_TYPE_BUY, user=self, order_time=datetime.now()
            )
        )

    def sell(self, price: float) -> None:
        """sell buy"""
        self.market.transaction(
            incoming_order=Order(
                price=price, order_type=OrderType.ORDER_TYPE_SELL, user=self, order_time=datetime.now()
            )
        )


# do your game
m = Market()

user1 = User(uid="000001", meta={"username": "user1"}, market=m)
user2 = User(uid="000002", meta={"username": "user2"}, market=m)

user1.sell(10)
print("buys = ", m.buy_orders)
print("sells = ", m.sell_orders)

user2.buy(11)

print("buys = ", m.buy_orders)
print("sells = ", m.sell_orders)

user1.sell(100)
print("buys = ", m.buy_orders)
print("sells = ", m.sell_orders)

user2.buy(99)
print("buys = ", m.buy_orders)
print("sells = ", m.sell_orders)

user2.buy(101)
print("buys = ", m.buy_orders)
print("sells = ", m.sell_orders)

user1.sell(98)
print("buys = ", m.buy_orders)
print("sells = ", m.sell_orders)
