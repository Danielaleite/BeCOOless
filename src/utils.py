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


def parse_current_items_list(current_items):
    """
    Extracts necessary information from app's current item list.

    Args:
        current_items: List of current items on app

    Returns:
        Dictionary of all parsed current intentions.
    """
    # Dictionary of all parsed current intentions
    current_items_dict = dict()

    for item in current_items:
        item_dict = dict()

        # Get category
        item_dict["name"] = re.sub(HTML_REGEX, "", item["nm"], count=LARGE_NUMBER, flags=re.IGNORECASE)
        item_dict["category"] = re.search(HTML_REGEX, item["cat"], re.IGNORECASE)
        item_dict["carbon"] = re.search(HTML_REGEX, item["carbon"], re.IGNORECASE)
        item_dict["cost"] = re.search(HTML_REGEX, item["cost"], re.IGNORECASE)
        item_dict["location"] = re.search(HTML_REGEX, item["loc"], re.IGNORECASE)
        item_dict["weight"] = 0

        kg = re.search(KG_REGEX, item["w"], re.IGNORECASE)
        if kg is not None:
            kg = kg[0].strip()
            kg = float(kg.split(" ")[0].strip())
            item_dict["weight"] += kg * 1000

        grams = re.search(GRAMS_REGEX, item["w"], re.IGNORECASE)
        if grams is not None:
            grams = grams[0].strip()
            grams = float(grams.split(" ")[0].strip())
            item_dict["weight"] += grams



        # Add current task to the dictionary of all parsed current intentions
        current_items_dict.setdefault(item_dict["id"], [])
        current_items_dict[item_dict["id"]].append(item_dict)

    return current_items_dict


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


def flatten_intentions(projects):
    for goal in projects:
        for task in goal["ch"]:
            if "ch" in task:
                goal["ch"].extend(task["ch"])
                del task["ch"]
    return projects


def get_final_output(item_list, round_param, points_per_hour, user_datetime):
    """
    Input is list of items
    Outputs list of items for today with fields:
        id, nm, lm, parentId, pcp, est, val (=reward)
    """

    def get_human_readable_name(item):
        item_name = item["nm"]

        # Remove #date regex
        item_name = re.sub(fr"#\s*{DATE_REGEX}", "", item_name, re.IGNORECASE)

        # Remove deadline
        item_name = re.sub(DEADLINE_REGEX, "", item_name, re.IGNORECASE)

        # Remove time estimation
        item_name = re.sub(TIME_EST_REGEX, "", item_name, re.IGNORECASE)

        # Remove importance
        item_name = re.sub(IMPORTANCE_REGEX, "", item_name, re.IGNORECASE)

        # Remove essential
        item_name = re.sub(ESSENTIAL_REGEX, "", item_name, re.IGNORECASE)

        print(f'item: {item}')
        # Remove tags
        for tag in TAGS:
            tag_regex = get_tag_regex(tag)
            item_name = re.sub(tag_regex, "", item_name, re.IGNORECASE)

        item_name = item_name.strip()

        if len(re.sub(OUTPUT_GOAL_CODE_REGEX, "", item_name).strip()) == 0:
            raise NameError(f"Item {item['nm']} has no name!")

        # Append time information
        hours, minutes = item["est"] // 60, item["est"] % 60

        item_name += " (takes about "
        if hours > 0:
            if hours == 1:
                item_name += f"1 hour"
            else:
                item_name += f"{hours} hours"
        if minutes > 0:
            if hours > 0:
                item_name += " and "
            if minutes == 1:
                item_name += f"1 minute"
            else:
                item_name += f"{minutes} minutes"

        if hasattr(item, "deadline_datetime") and \
                item["deadline_datetime"] is not None:
            item_name += ", due on "

            td = item["deadline_datetime"] - user_datetime
            if td.days < 7:
                weekday = item["deadline_datetime"].weekday()
                item_name += WEEKDAYS[weekday]
            else:
                item_name += str(item["deadline_datetime"])[:-3]

        item_name += ")"

        return item_name

    keys_needed = ["id", "nm", "lm", "parentId", "pcp", "est", "val", "imp"]

    # for now only look at first dictionary
    current_keys = set(item_list[0].keys())
    extra_keys = list(current_keys - set(keys_needed))
    missing_keys = list(set(keys_needed) - current_keys)

    for item in item_list:

        item["nm"] = get_human_readable_name(item)

        if points_per_hour:
            item["val"] = str(round(item["pph"], round_param)) + '/h'
        else:
            item["val"] = round(item["val"], round_param)

        for extra_key in extra_keys:
            if extra_key in item:
                del item[extra_key]

        for missing_key in missing_keys:
            if missing_key not in item:
                item[missing_key] = None

    return item_list





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


