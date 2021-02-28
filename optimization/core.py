"""Core functionality for optimizing shopping lists."""

import cvxpy as cp
import numpy as np


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


def print_solution(amounts, price, co2_emission, description=""):
    """Print solution properties to command line."""
    print(f"Solution: {description}")
    print("\tamounts:       ", amounts)
    print("\tprice:         ", price)
    print("\tCO₂ emissions: ", co2_emission)
