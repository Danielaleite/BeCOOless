import numpy as np
import re

from collections import deque
from copy import deepcopy
from datetime import datetime, timedelta
from math import ceil
from string import digits

KG_REGEX = r"(?:^||>)\(?\s*\d+[\.\,]*\d*\s*(?:kg)s?\)?(?:|[^\da-z.]|$)"
HTML_REGEX = r"<(\/|)(b|i|u)>"
GRAMS_REGEX = r"(?:^||>)\(?\s*\d+[\.\,]*\d*\s*(?:grams)s?\)?(?:|[^\da-z.]|$)"


def extract_category_pool(category, offer):
    """Extract all products from data which belong to one ``category``."""
    category_pool = {
        product_id: product_info
        for product_id, product_info in offer.items()
        if product_info["category"] == category
    }

    return category_pool

def flatten(iterable):
    """Recursively iterate lists and tuples.
    """
    for elm in iterable:
        if isinstance(elm, (list, tuple)):
            for relm in flatten(elm):
                yield relm
        else:
            yield elm


def parse_current_items_list(db, current_categories,location):
    """
    Extracts necessary information from app's current item list.

    Args:
        current_categories: List of current categories in list
        location: Location to shop
    Returns:
        Dictionary of all parsed current intentions.
    """

    search_space = []
    prices = []
    carbons = []
    units = []
    for category in current_categories:
        cursor = db.stock_table.find({
            "$and": [
                {"Location": location},
                {"Category": category}
            ]
        })
        item = [c for c in cursor]
        search = [c['Product Name'] for c in item]
        unit = [c['Unit'] for c in item]
        price = [c['Price'] for c in item]
        carbon = [c['CO2'] for c in item]
        search_space.append(search)
        units.extend((unit))
        prices.extend(price)
        carbons.extend(carbon)

    target_amounts = []
    for category in current_categories:
        target_amounts.append(current_categories[category])

    new_units = []
    for unit in units:
        if unit[-2:] == "KG":
            new_units.extend([float(unit[:-2])])
        elif unit[-1] == "G":
            new_units.extend([float(unit[:-1])])

    target_amounts = tuple(target_amounts)
    search_space = tuple(search_space)
    prices = tuple(prices)
    carbons = tuple(carbons)
    units = tuple(new_units)

    print(f'Search Space: {search_space}')
    print(f'Units: {units}')
    print(f'Amounts: {target_amounts}')
    print(f'Prices: {prices}')
    print(f'CO2 Emissions: {carbons}')

    # print(type(search_space))
    # print(type(units))
    # print(type(target_amounts))
    # print(type(prices))
    # print(type(carbons))
    parsed_dict = {
        "search": search_space,
        "units": units,
        "amounts": target_amounts,
        "prices": prices,
        "carbons": carbons
    }

    return parsed_dict


def delete_sensitive_data(projects):
    def recursive_deletion(super_item):

        # Delete item name
        del super_item["nm"]

        # TODO: What is "no"
        try:
            del super_item["no"]
        except:
            pass

        # Delete sensitive data recursively (if item has children nodes)
        if "ch" in super_item.keys():

            for item in super_item["ch"]:
                recursive_deletion(item)

    # Make deep copy of the complete data dictionary
    items = deepcopy(projects)

    # Delete sensitive data recursively
    for item in items:
        recursive_deletion(item)

    return items



def get_final_output(db, search_space, output, flag,rounding, location):
    """
    Input is list of items
    Outputs list of items for today with fields:
        id, nm, lm, parentId, pcp, est, val (=reward)
    """

    if flag == "optimal_price":
        return \
            {
                "price": round(output["price"],int(rounding)),
                "carbon": round(output["carbon"], int(rounding))
            }

    elif flag == "optimal_co2":
        final_dict = dict()
        for i, category in enumerate(search_space):
            for j, item in enumerate(category):
                if output["amount"][i][j] > 0:
                    cursor = db.stock_table.find({
                        "$and": [
                            {"Location": location},
                            {"Product Name": item}
                        ]
                    })
                    item_db = [c for c in cursor]
                    # print(f'Item_db:{item_db}')
                    final_dict[item] = {"amount": output["amount"][i][j],
                                        "price": round(output["amount"][i][j] * item_db[0]["Price"],2),
                                        "carbon": round(output["amount"][i][j] * item_db[0]["CO2"],2)}
        final_dict["price"] = round(output["price"], int(rounding))
        final_dict["carbon"] = round(output["carbon"], int(rounding))
        return final_dict




def parse_error_info(error):
    """
    Removes personal info and returns the exception info.

    Args:
        error: Error message as string

    Returns:
        Exception info without personal data.
    """
    return error.split(": ")[-1]



def store_log(db_collection, log_dict, **params):
    """
    Stores the provided log dictionary in the DB collection with the additional
    (provided) parameters.

    Args:
        db_collection:
        log_dict:
        **params: Parameters to be stored, but NOT saved in the provided dict.
                  If you want to store the changes, then "catch" the returned
                  object after calling this function.

    Returns:
        Log dictionary with the existing + new parameters!
    """
    # Avoid overlaps
    log_dict = dict(log_dict)

    # Store additional info in the log dictionary
    for key in params.keys():
        log_dict[key] = params[key]

    log_dict["duration"] = str(datetime.now() - log_dict["start_time"])
    log_dict["timestamp"] = datetime.now()

    db_collection.insert_one(log_dict)  # Store info in DB collection

    return log_dict


