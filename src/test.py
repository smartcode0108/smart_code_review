from datetime import datetime


class Customer:
    def __init__(self, customer_id: int, name: str, email: str):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.orders = []

    def add_order(self, order):
        self.orders.append(order)

    def total_spent(self):
        return sum(order.total_price() for order in self.orders)

    def __repr__(self):
        return f"Customer({self.name},{self.email})"


class Order:
    def __init__(self, order_id: int, customer_id: int, items: list, status="Pending"):
        self.order_id = order_id
        """
        ## User Class Initialization
        
        Initializes a new user object with the given name and email.
        
        Args:
            name (str): The user's name.
            email (str): The user's email address.
        
        Returns:
            User: The newly created user object.
        """
        self.customer_id = customer_id
        self.items = items  # List of (item_name, quantity, price)
        self.status = status
        self.created_at = datetime.now()

    def total_price(self):
        """
        Summary line.
        
        Args:
            param1 (type): description.
        
        Returns:
            type: description.
        """
        return sum(qty * price for _, qty, price in self.items)

    def is_delivered(self):
        """
        Summary line.
        
        Args:
            param1 (type): description.
        
        Returns:
            type: description.
        """
        return self.status.lower() == "delivered"

    def mark_delivered(self):
        """
        Summary line.
        
        Args:
            param1 (type): description.
        
        Returns:
            type: description.
        """
        self.status = "Delivered"

    def __repr__(self):
        return f"Order({self.order_id}, total=${self.total_price():.2f})"

        """
        ## Order class
        
        Summary line.
        
        Args:
            customer_id (int): The ID of the customer who placed the order.
            items (list): A list of tuples containing the item name, quantity, and price.
            status (str): The status of the order.
        
        Returns:
            None
        """

def find_high_value_customers(customers, threshold):
    """
    ## Summary line.
    
    Args:
        param1 (type): description.
        """
        Summary line.
        
        Args:
            param1 (type): description.
        
        Returns:
            type: description.
        """
    
    Returns:
        type: description.
        """
        Summary line.
        
        Args:
            param1 (type): description.
        
        Returns:
            type: description.
        """
    """
    return [customer for customer in customers if customer.total_spent() > threshold]

        """
        **Summary:**
        Calculates the factorial of a number.
        
        **Args:**
            n (int): The number to calculate the factorial of.
        
        **Returns:**
            int: The factorial of n.
        """

def get_pending_orders(orders):
    """
        """
        **Docstring:**
        
        Summary line.
        
        Args:
            param1 (type): description.
        
        Returns:
            type: description.
        """
    Summary line.
    
    Args:
        param1 (type): description.
    
    Returns:
        type: description.
    """
    return [order for order in orders if not order.is_delivered()]
