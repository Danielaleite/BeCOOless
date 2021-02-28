"""Dummy data set to demo the tool's usefulness."""

import cvxpy as cp
import numpy as np

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


###############################################################################
#                            Optimization utilities                           #
###############################################################################


def constrain_elements_non_negative(variables):
    """Constrain each variable to  be ``>=0``. Return list of constraints."""
    return [var >= 0 for var in variables]


def constrain_match_shopping_list(category_count, target_amounts, amounts, units):
    """Return list of constrains such that chosen amounts fulfill the shopping order."""
    constraints = []

    start = 0

    for target, num_products in zip(target_amounts, category_count):
        end = start + num_products
        constraints.append(amounts[start:end] @ units[start:end] == target)
        start = end

    return constraints


def compute_cost(amounts, factors):
    """Evaluate the cost function by weighting amounts with factors."""
    return factors @ amounts


def minimize(objective, constraints):
    """Solves a Knapsack problem. Modifies variables of the objective function."""
    problem = cp.Problem(cp.Minimize(objective), constraints)
    problem.solve(solver="ECOS_BB")

    return problem.value


def group_by_categories(product_ids, flat_vector):
    """Recover the category substructure of a flat vector."""
    transformed_vector = []

    num_products_in_category = [len(ids) for ids in product_ids]

    start = 0
    for num_products in num_products_in_category:
        end = start + num_products
        transformed_vector.append(flat_vector[start:end].tolist())
        start = end

    return transformed_vector


def solve_optimal_price(product_ids, target_amounts, units, prices, co2_emissions):
    """Realize shopping list at lowest price.

    Returns the found solution (amounts to purchase from each product), its price, and
    its co2 emission.
    """
    num_variables = sum(len(products) for products in product_ids)

    amounts = cp.Variable(num_variables, integer=True)

    constraints = []

    # non-negative amounts
    constraints += constrain_elements_non_negative(amounts)

    # must fulfill shopping list
    category_count = [len(products) for products in product_ids]

    constraints += constrain_match_shopping_list(
        category_count, target_amounts, amounts, units
    )

    # objective
    cost_price = compute_cost(amounts, prices)

    # solve optimization
    solution_price = minimize(cost_price, constraints)
    solution_amounts = np.round(amounts.value).astype(np.int32)
    solution_co2_emissions = compute_cost(solution_amounts, co2_emissions)

    solution_amounts = group_by_categories(product_ids, solution_amounts)

    return solution_amounts, solution_price, solution_co2_emissions


def print_solution(amounts, price, co2_emission, description=""):
    """Print solution properties to command line."""
    print(f"Solution: {description}")
    print("\tamounts:       ", amounts)
    print("\tprice:         ", price)
    print("\tCO₂ emissions: ", co2_emission)


def solve_optimal_co2(
    product_ids,
    target_amounts,
    units,
    prices,
    co2_emissions,
    user_threshold,
    cheap_price,
):
    num_variables = sum(len(products) for products in product_ids)
    amounts = cp.Variable(num_variables, integer=True)

    # constraints
    constraints = []

    # non-negative amounts
    constraints += constrain_elements_non_negative(amounts)

    # must fulfill shopping list
    category_count = [len(products) for products in product_ids]

    constraints += constrain_match_shopping_list(
        category_count, target_amounts, amounts, units
    )

    # must be lower than threshold-ed cost
    cost_price = compute_cost(amounts, prices)
    constraints.append(cost_price <= (1 + user_threshold) * cheap_price)

    # objective
    cost_co2_emissions = compute_cost(amounts, co2_emissions)

    # solve optimization
    solution_co2_emissions = minimize(cost_co2_emissions, constraints)
    solution_amounts = np.round(amounts.value).astype(np.int32)
    solution_price = compute_cost(solution_amounts, prices)

    solution_amounts = group_by_categories(product_ids, solution_amounts)

    return solution_amounts, solution_price, solution_co2_emissions


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
