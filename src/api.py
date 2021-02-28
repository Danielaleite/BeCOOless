from optimization.core import *

# For gamification. To give points

def assign_points(current_items, threshold):
    return [0*threshold for _ in range(len(current_items))]

def function_call(flag, search_space, target_amounts, units, prices, co2_emissions, cost_threshold=None, cheap_price=None):
    if flag == "optimal_price":
        cheap_amounts, cheap_price, cheap_co2_emission = solve_optimal_price(
            search_space, target_amounts, units, prices, co2_emissions
        )
        final = {
            "amount": tuple(cheap_amounts),
            "price": cheap_price,
            "carbon": cheap_co2_emission
        }

    elif flag == "optimal_co2":
        print(f"Cheap Price: {cheap_price}")
        print(f'Threshold: {cost_threshold}')
        green_amounts, green_price, green_co2_emission = solve_optimal_co2(
            search_space, target_amounts, units, prices, co2_emissions, cost_threshold, cheap_price)

        final = {
            "amount": tuple(green_amounts),
            "price": green_price,
            "carbon": green_co2_emission
        }

    return final