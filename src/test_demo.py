

def multiply_and_add(x, y):
    return x * y + x


def main():
    numbers = [1, 2, 3, 4]
    results = []
    for num in numbers:
        results.append(multiply_and_add(num, 2))
    print("Results:", results)


def test_main():
    numbers = [1, 2, 3, 4]
    expected = [1 * 2 + 1, 2 * 2 + 2, 3 * 2 + 3, 4 * 2 + 4]
    for i in range(len(numbers)):
        assert multiply_and_add(numbers[i], 2) == expected[i]


main()
test_main()
