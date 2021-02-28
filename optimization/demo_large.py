"""Demo on a larger data set."""

from data import offer
from demo_small import demo
from utils import compute_savings

if __name__ == "__main__":

    thresholds = [0.03, 0.04, 0.05, 0.1, 0.15]

    shopping_list = [
        ("melon", 1),
        ("oranges", 5),
        ("lettuce", 1),
        ("pepper", 2),
        ("eggs", 10),
        ("potatoes", 10),
        ("chicken", 1),
        ("pork", 1),
        ("beef", 1),
    ]

    for threshold in thresholds:
        (
            (_, cheap_price, cheap_co2_emission),
            (_, green_price, green_co2_emission),
        ) = demo(shopping_list, offer, threshold, verbose=False)

        compute_savings(
            cheap_price,
            cheap_co2_emission,
            green_price,
            green_co2_emission,
            verbose=True,
        )
