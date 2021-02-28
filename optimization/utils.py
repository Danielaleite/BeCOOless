"""Utility functions for evaluating optimization outputs."""


def compute_savings(
    cheap_price, cheap_co2_emission, green_price, green_co2_emission, verbose=False
):
    """Compute additional expenses and CO₂ savings. Optionally print to command line."""
    price_increase = (green_price - cheap_price) / cheap_price
    co2_savings = (cheap_co2_emission - green_co2_emission) / cheap_co2_emission

    if verbose:
        print(
            f"Spend {100 * price_increase:.1f}% more money, "
            + f"save {100 * co2_savings:.1f}% CO₂ emissions."
        )

    return price_increase, co2_savings
