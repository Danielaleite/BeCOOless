"""Dummy data set to demo the tool's usefulness."""

import pandas as pd
import os
dummy_shopping_list = [
    ("apples", 3),
    ("bananas", 2),
]

# user allows 5% more budget to optimize for CO2
dummy_user_tol = 0.05

offer = {
    "conventional apple": {"category": "apples", "unit": 1, "price": 1.0, "CO2": 5.0,},
    "bio apple": {"category": "apples", "unit": 1, "price": 2.0, "CO2": 4.0,},
    "conventional banana": {
        "category": "bananas",
        "unit": 1,
        "price": 0.5,
        "CO2": 10.0,
    },
    "bio banana": {"category": "bananas", "unit": 1, "price": 0.75, "CO2": 9.0,},
    "beef": {"category": "beef", "unit": 1, "price": 2.99, "CO2": 29,},
    "beef south america": {"category": "beef", "unit": 1, "price": 3.99, "CO2": 41,},
    "pork": {"category": "pork", "unit": 1, "price": 3.99, "CO2": 6,},
    "pork imported": {"category": "pork", "unit": 1, "price": 3.70, "CO2": 6.5,},
    "bio chicken": {"category": "chicken", "unit": 1, "price": 3.99, "CO2": 2.8,},
    "chicken": {"category": "chicken", "unit": 1, "price": 2.99, "CO2": 3.7,},
    "eggs": {"category": "eggs", "unit": 1, "price": 1.49, "CO2": 2.0,},
    "bio eggs": {"category": "eggs", "unit": 1, "price": 2.19, "CO2": 1.5,},
    "carrot": {"category": "carrot", "unit": 1, "price": 0.99, "CO2": 0.10,},
    "carrot": {"category": "carrot", "unit": 1, "price": 1.49, "CO2": 0.08,},
    "lettuce": {"category": "lettuce", "unit": 1, "price": 0.99, "CO2": 1.05,},
    "bio lettuce": {"category": "lettuce", "unit": 1, "price": 1.79, "CO2": 0.26,},
    "open field lettuce": {
        "category": "lettuce",
        "unit": 1,
        "price": 1.99,
        "CO2": 0.14,
    },
    "melon": {"category": "melon", "unit": 1, "price": 2.99, "CO2": 1.0,},
    "bio melon": {"category": "melon", "unit": 1, "price": 3.99, "CO2": 0.3,},
    "oranges": {"category": "oranges", "unit": 1, "price": 1.99, "CO2": 0.35,},
    "bio oranges": {"category": "oranges", "unit": 1, "price": 2.49, "CO2": 0.25,},
    "pepper": {"category": "pepper", "unit": 1, "price": 0.99, "CO2": 3.5,},
    "pepper": {"category": "pepper", "unit": 1, "price": 1.99, "CO2": 0.48,},
    "potatoes": {"category": "potatoes", "unit": 1, "price": 1.49, "CO2": 0.35,},
    "bio potatoes": {"category": "potatoes", "unit": 1, "price": 1.99, "CO2": 0.18,},
    "local potatoes": {
        "category": "potatoes",
        "unit": 1,
        "price": 2.25,
        "CO2": 0.12,
    },
}

if __name__ == '__main__':
    df = pd.DataFrame(columns=["Location", "Category", "Product Name", "Price", "Unit", "CO2"])
    for i, prod in enumerate(offer):
        # print(prod)
        loc = "Rewe"
        cat = offer[prod]["category"]
        price = offer[prod]["price"]
        unit = offer[prod]["unit"]
        unit = str(unit) + 'KG'
        carbon = offer[prod]["CO2"]
        df.loc[i] = [loc, cat, prod, price, unit, carbon]
    df.to_csv(os.getcwd() + '/data_gen/StockIn  fo.csv', index=False)