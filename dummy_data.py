"""Dummy data set to demo the tool's usefulness."""

import pprint

import cvxpy as cp
import numpy as np

dummy_shopping_list = [
    ("apples", 3),
    ("bananas", 2),
]

# user allows 5% more budget to optimize for CO2
dummy_user_threshold = 0.25

dummy_offer = {
    "conventional apple": {
        "category": "apples",
        "unit": 1,
        "price": 1.0,
        "CO2": 5.0,
    },
    "bio apple": {
        "category": "apples",
        "unit": 1,
        "price": 2.0,
        "CO2": 4.0,
    },
    "conventional banana": {
        "category": "bananas",
        "unit": 1,
        "price": 0.5,
        "CO2": 10.0,
    },
    "bio banana": {
        "category": "bananas",
        "unit": 1,
        "price": 0.75,
        "CO2": 9.0,
    },
    "bio orange": {
        "category": "oranges",
        "unit": 1,
        "price": 1.5,
        "CO2": 15,
    },
}


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
    product_ids = []
    units = []
    prices = []
    CO2_emissions = []

    for category in categories:
        category_product_ids = []
        category_units = []
        category_prices = []
        category_CO2_emissions = []

        category_space = pool[category]
        for product_id, product_info in category_space.items():
            category_product_ids.append(product_id)
            category_units.append(product_info["unit"])
            category_prices.append(product_info["price"])
            category_CO2_emissions.append(product_info["CO2"])

        product_ids.append(category_product_ids)
        units.append(category_units)
        prices.append(category_prices)
        CO2_emissions.append(category_CO2_emissions)

    return product_ids, units, prices, CO2_emissions


def constrain_elements_non_negative(variables):
    """Constrain each variable to  be ``>=0``. Return list of constraints."""
    return [var >= 0 for var in variables]


def solve_optimal_price(product_ids, target_amounts, units, prices, CO2_emissions):
    num_variables = sum(len(products) for products in product_ids)

    amounts = cp.Variable(num_variables, integer=True)

    # constraints
    constraints = []

    constraints += constrain_elements_non_negative(amounts)

    units_flat = np.array(sum(units, []))

    # must fulfill shopping list
    start = 0
    for category_idx, products in enumerate(product_ids):
        num_products = len(products)
        constraints.append(
            amounts[start : start + num_products]
            @ units_flat[start : start + num_products]
            == target_amounts[category_idx]
        )
        start += num_products

    prices_flat = np.array(sum(prices, []))
    cost = prices_flat @ amounts

    knapsack_problem = cp.Problem(cp.Minimize(cost), constraints)
    knapsack_problem.solve(solver="ECOS_BB")

    cost_value = knapsack_problem.value
    solution = np.round(amounts.value).astype(np.int32)

    CO2_emissions_flat = np.array(sum(CO2_emissions, []))
    CO2_cost_value = CO2_emissions_flat @ solution

    solution_transformed = []
    start = 0

    for category_idx, products in enumerate(product_ids):
        num_products = len(products)
        solution_transformed.append(solution[start : start + num_products].tolist())
        start += num_products

    print("Optimal amounts found by solver:", solution_transformed)
    print("Optimal cost value found by solver:", cost_value)
    print("CO2 cost:", CO2_cost_value)

    return solution_transformed, cost_value, CO2_cost_value


def solve_optimal_CO2(
    product_ids,
    target_amounts,
    units,
    prices,
    CO2_emissions,
    user_threshold,
    cheapest_cost,
):
    num_variables = sum(len(products) for products in product_ids)
    amounts = cp.Variable(num_variables, integer=True)

    # constraints
    constraints = []

    # non-positive product counts
    constraints += constrain_elements_non_negative(amounts)

    units_flat = np.array(sum(units, []))

    # must fulfill shopping list
    start = 0
    for category_idx, products in enumerate(product_ids):
        num_products = len(products)
        constraints.append(
            amounts[start : start + num_products]
            @ units_flat[start : start + num_products]
            == target_amounts[category_idx]
        )
        start += num_products

    # must be lower than threshold-ed cost
    prices_flat = np.array(sum(prices, []))

    cost = prices_flat @ amounts
    constraints.append(cost <= (1 + user_threshold) * cheapest_cost)

    # set up objective
    CO2_emissions_flat = np.array(sum(CO2_emissions, []))
    CO2_cost = CO2_emissions_flat @ amounts

    knapsack_problem = cp.Problem(cp.Minimize(CO2_cost), constraints)
    knapsack_problem.solve(solver="ECOS_BB")

    CO2_cost_value = knapsack_problem.value
    solution = np.round(amounts.value).astype(np.int32)

    cost_value = solution @ prices_flat

    solution_transformed = []
    start = 0

    for category_idx, products in enumerate(product_ids):
        num_products = len(products)
        solution_transformed.append(solution[start : start + num_products].tolist())
        start += num_products

    print("CO2-optimal amounts found by solver:", solution_transformed)
    print("CO2-optimal cost of shopping list:", cost_value)
    print("CO2-optimal cost value found by solver:", CO2_cost_value)

    return solution_transformed, cost_value, CO2_cost_value


def demo():
    """Run a demo."""
    ############################################################################
    #                         Prepare input to optimizer                       #
    ############################################################################
    target_categories, target_amounts = extract_categories_and_amounts(
        dummy_shopping_list
    )
    print(f"User wants to buy:")
    for category, amount in zip(target_categories, target_amounts):
        print(f"\t{category}: {amount}")

    # build pools of products to search over
    pool = create_pool(target_categories, dummy_offer)
    print("Search space:\n", pprint.pformat(pool))

    # pull out the attributes category-wise for optimization
    product_ids, units, prices, CO2_emissions = extract_optimization_input(
        target_categories, pool
    )

    print("Target categories:", target_categories)
    print("Target amounts:", target_amounts)
    print("Products:", product_ids)
    print("Units:", units)
    print("Prices:", prices)
    print("CO2:", CO2_emissions)

    ############################################################################
    #                    Optimal solution in terms of money                    #
    ############################################################################
    cheapest_amounts, cheapest_cost, cheapest_CO2_emission = solve_optimal_price(
        product_ids, target_amounts, units, prices, CO2_emissions
    )

    ############################################################################
    #                     Optimal solution in terms of CO2                     #
    ############################################################################
    CO2_amounts, CO2_cost, CO2_emission = solve_optimal_CO2(
        product_ids,
        target_amounts,
        units,
        prices,
        CO2_emissions,
        dummy_user_threshold,
        cheapest_cost,
    )


if __name__ == "__main__":
    demo()
