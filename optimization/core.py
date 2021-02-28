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
    """Restore category substructure of a flat vector.

    Used to process the optimization output.

    Args:
        product_ids (list(list)): Each entry contains the products that match
            the associated category.
        flat_vector (numpy.array): Flattened vector that has the same number
            of elements as the concatenated products in ``product_ids``.

    Returns:
        list(list): Reshaped version of ``flat_vector`` with the same structure
            as ``product_ids``.
    """
    transformed_vector = []

    num_products_in_category = [len(ids) for ids in product_ids]

    start = 0
    for num_products in num_products_in_category:
        end = start + num_products
        transformed_vector.append(flat_vector[start:end].tolist())
        start = end

    return transformed_vector


def solve_optimal_price(product_ids, target_amounts, units, prices, co2_emissions):
    """Find shopping list with lowest price.

    Solves a constrained optimization problem under the hood.

    Args:
        product_ids (list(list)): Each category is comprised of multiple products.
            Entry ``i`` of ``product_ids`` contains the search pool for category ``i``,
            i.e. is a list of products that belong to category ``i``.
        target_amounts (tuple or list): Mapping from category to desired amount.
            ``target_amounts[i]`` is the amount of purchases for category ``i``.
        units (numpy.array): Flattened units per amount for the pool of products.
        prices (numpy.array): Flattened prices for the pool of products.
        co2_emissions (numpy.array): Flattened CO₂ emissions for the pool of products.

    Returns:
        (amounts, price, co2_emissions)

        - ``amounts`` has the same structure as ``product_ids`` and contains the counts
          with which the corresponding product should be purchased.
        - price (float) is the shopping list's price.
        - co2_emission (float) is the shopping list's CO₂ footprint.
    """
    category_count = [len(products) for products in product_ids]

    num_variables = sum(category_count)
    amounts = cp.Variable(num_variables, integer=True)

    constraints = constrain_elements_non_negative(
        amounts
    ) + constrain_match_shopping_list(category_count, target_amounts, amounts, units)

    cost_price = compute_cost(amounts, prices)

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
    threshold,
    cheap_price,
):
    """Find shopping list with lowest CO₂ footprint. Budget is extended by a threshold.

    Solves a constrained optimization problem under the hood.

    Args:
        product_ids (list(list)): Each category is comprised of multiple products.
            Entry ``i`` of ``product_ids`` contains the search pool for category ``i``,
            i.e. is a list of products that belong to category ``i``.
        target_amounts (tuple or list): Mapping from category to desired amount.
            ``target_amounts[i]`` is the amount of purchases for category ``i``.
        units (numpy.array): Flattened units per amount for the pool of products.
        prices (numpy.array): Flattened prices for the pool of products.
        co2_emissions (numpy.array): Flattened CO₂ emissions for the pool of products.
        threshold (float): Tolerance by which the budget may be extended.
        cheap_price (float): Budget (e.g. the cheapest price to realize the shopping
            list).

    Returns:
        (amounts, price, co2_emissions)

        - ``amounts`` has the same structure as ``product_ids`` and contains the counts
          with which the corresponding product should be purchased.
        - price (float) is the shopping list's price.
        - co2_emission (float) is the shopping list's CO₂ footprint.
    """
    category_count = [len(products) for products in product_ids]

    num_variables = sum(category_count)
    amounts = cp.Variable(num_variables, integer=True)

    constraints = constrain_elements_non_negative(
        amounts
    ) + constrain_match_shopping_list(category_count, target_amounts, amounts, units)

    # must be lower than original budget plus threshold
    cost_price = compute_cost(amounts, prices)
    constraints.append(cost_price <= (1 + threshold) * cheap_price)

    cost_co2_emissions = compute_cost(amounts, co2_emissions)

    solution_co2_emissions = minimize(cost_co2_emissions, constraints)
    solution_amounts = np.round(amounts.value).astype(np.int32)
    solution_price = compute_cost(solution_amounts, prices)
    solution_amounts = group_by_categories(product_ids, solution_amounts)

    return solution_amounts, solution_price, solution_co2_emissions
