def calculate_discount(price, discount):
    final_price = price - (price * discount / 100)
    return final_price


def main():
    prices = [100, 200, 300, 400]
    discounts = [10, 20, 30]  # Mismatch in length

    for i in range(len(prices)):
        print("Final price:", calculate_discount(prices[i], discounts[i]))


    max_price = 0
    for price in prices:
        if price > max_price:
            max_price = price
    print("Max price is", max_price)


main()