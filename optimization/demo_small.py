"""Dummy data set to demo the tool's usefulness."""

import numpy as np

from core import solve_optimal_co2, solve_optimal_price

###############################################################################
#                         Data pre-processing utilities                       #
###############################################################################


def extract_categories_and_amounts(shopping_list):
    """Extract categories and amounts into separate lists."""
    categories, amounts = zip(*shopping_list)

    if len(set(categories)) != len(categories):
        raise ValueError("Duplicate categories in shopping list")

    return categories, amounts


def extract_category_pool(category, offer):
    """Extract all products from data which belong to one ``category``."""
    category_pool = {
        product_id: product_info
        for product_id, product_info in offer.items()
        if product_info["category"] == category
    }

    return category_pool


def create_pool(categories, offer):
    """Create a collection of category pools."""
    pool = {category: extract_category_pool(category, offer) for category in categories}

    return pool


def extract_optimization_input(categories, pool):
    """Flatten the search space's relevant quantities into vectors."""
    product_ids = []
    units = []
    prices = []
    co2_emissions = []

    for category in categories:
        category_product_ids = []

        category_space = pool[category]
        for product_id, product_info in category_space.items():
            category_product_ids.append(product_id)
            units.append(product_info["unit"])
            prices.append(product_info["price"])
            co2_emissions.append(product_info["co2"])

        product_ids.append(category_product_ids)

    units = np.array(units)
    prices = np.array(prices)
    co2_emissions = np.array(co2_emissions)

    return product_ids, units, prices, co2_emissions


def print_solution(amounts, price, co2_emission, description=""):
    """Print solution properties to command line."""
    print(f"Solution: {description}")
    print("\tamounts:       ", amounts)
    print("\tprice:         ", price)
    print("\tCO₂ emissions: ", co2_emission)


def demo(shopping_list, offer, threshold, verbose=False):
    """Run a demo."""

    ############################################################################
    #                         Prepare input to optimizer                       #
    ############################################################################
    target_categories, target_amounts = extract_categories_and_amounts(shopping_list)

    # build pools of products to search over
    pool = create_pool(target_categories, offer)

    # pull out the attributes category-wise for optimization
    product_ids, units, prices, co2_emissions = extract_optimization_input(
        target_categories, pool
    )

    if verbose:
        print("Optimization-relevant information:")
        print("\tTarget categories: ", target_categories)
        print("\tTarget amounts:    ", target_amounts)
        print("\tSearch space:      ", product_ids)
        print("\tUnits per amount:  ", units)
        print("\tPrices:            ", prices)
        print("\tCO₂ emissions:     ", co2_emissions)

        print("")

        print("Shopping list :", shopping_list)
        print("Products      :", product_ids)

        print("")

    ############################################################################
    #                    Optimal solution in terms of money                    #
    ############################################################################
    cheap_amounts, cheap_price, cheap_co2_emission = solve_optimal_price(
        product_ids, target_amounts, units, prices, co2_emissions
    )

    if verbose:
        print_solution(
            cheap_amounts,
            cheap_price,
            cheap_co2_emission,
            description="(optimal price)",
        )
        print("")

    ############################################################################
    #                     Optimal solution in terms of CO₂                     #
    ############################################################################
    green_amounts, green_price, green_co2_emission = solve_optimal_co2(
        product_ids,
        target_amounts,
        units,
        prices,
        co2_emissions,
        threshold,
        cheap_price,
    )

    if verbose:
        print_solution(
            green_amounts,
            green_price,
            green_co2_emission,
            description=f"(CO₂-optimized with threshold {threshold})",
        )

    return (
        (cheap_amounts, cheap_price, cheap_co2_emission),
        (green_amounts, green_price, green_co2_emission),
    )


if __name__ == "__main__":

    dummy_shopping_list = [
        ("apples", 3),
        ("bananas", 2),
    ]

    # user allows 25% more budget to optimize for CO₂
    dummy_threshold = 0.25

    dummy_offer = {
        "conventional apple": {
            "category": "apples",
            "unit": 1,
            "price": 1.0,
            "co2": 5.0,
        },
        "bio apple": {
            "category": "apples",
            "unit": 1,
            "price": 2.0,
            "co2": 4.0,
        },
        "conventional banana": {
            "category": "bananas",
            "unit": 1,
            "price": 0.5,
            "co2": 10.0,
        },
        "bio banana": {
            "category": "bananas",
            "unit": 1,
            "price": 0.75,
            "co2": 9.0,
        },
        "bio orange": {
            "category": "oranges",
            "unit": 1,
            "price": 1.5,
            "co2": 15,
        },
    }

    (
        (cheap_amounts, cheap_price, cheap_co2_emission),
        (green_amounts, green_price, green_co2_emission),
    ) = demo(dummy_shopping_list, dummy_offer, dummy_threshold, verbose=True)

    # verify correctness
    assert cheap_amounts == [[3, 0], [2, 0]]
    assert np.isclose(cheap_price, 4.0)
    assert np.isclose(cheap_co2_emission, 35.0)

    assert green_amounts == [[3, 0], [0, 2]]
    assert np.isclose(green_price, 4.5)
    assert np.isclose(green_co2_emission, 33.0)

    print("\nResults correct.")
