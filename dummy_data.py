"""Dummy data set to demo the tool's usefulness."""


dummy_shopping_list = [
    ("apples", 3),
    ("bananas", 2),
]

# user allows 5% more budget to optimize for CO2
dummy_user_tol = 0.05

offer = {
    "conventional apple": {
        "category": "apples",
        "amount": 1,
        "price": 1.0,
        "CO2": 5.0,
    },
    "bio apple": {
        "category": "apples",
        "amount": 1,
        "price": 2.0,
        "CO2": 4.0,
    },
    "conventional banana": {
        "category": "bananas",
        "amount": 1,
        "price": 0.5,
        "CO2": 10.0,
    },
    "bio banana": {
        "category": "bananas",
        "amount": 1,
        "price": 0.75,
        "CO2": 9.0,
    },
}
