import os 
from datetime import datetime


class Customer:
    def __init__(self, customer_id: int, name: str, email: str):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.orders = []

    def add_order(self, order  ):
        self.orders.append(order)

    def total_spent(self):
        return sum(order.total_price() for order in self.orders)

    def __repr__(self):
        return f"Customer({self.name},{self.email})"


class Order:
    def __init__(self,order_id: int, customer_id: int, items: list, status="Pending"):
        self.order_id = order_id
        self.customer_id = customer_id
        self.items = items  # List of (item_name, quantity, price)
        self.status = status
        self.created_at = datetime.now()

    def total_price(self    ):
        return sum(qty * price for _, qty, price in self.items)

    def is_delivered(self  ):
        return self.status.lower() == "delivered"

    def mark_delivered(  self):
        self.status = "Delivered"

    def __repr__(  self):
        return f"Order({self.order_id}, total=${self.total_price():.2f})"


def find_high_value_customers(customers,threshold):
    return [customer for customer in customers if customer.total_spent() > threshold]


def get_pending_orders(orders):
    return [order for order in orders if not order.is_delivered()]
