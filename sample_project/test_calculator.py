from calculator import calculate_total


def test_total():
    assert calculate_total(10, 3) == 30


def test_single_item():
    assert calculate_total(7, 1) == 7