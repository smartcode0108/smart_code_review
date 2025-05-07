import sqlite3


def get_user_by_email(email):
    """
    Summary line.
    
    Args:
        email (str): The user's email address.
    
    Returns:
        dict: A dictionary containing the user data.
    """
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE email = '{email}'"
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()
    return user


def send_welcome_email(user):
    """
    Summary:
    Sends an email with a greeting message.
    
    Args:
        user (dict): A dictionary containing user information, including name and email address.
    
    Returns:
        None
    """
    subject = "Welcome!"
    body = f"Hi {user['name']}, we're glad to have you."
    email_address = user["email"]
    print(f"Sending email to {email_address}")
    print(f"Subject: {subject}")
    print(f"Body: {body}")
