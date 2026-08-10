import re


# We start with a function like this so that we can change it further down the line to a more broad amount of countries.
def verify_phone_number (number:str) -> bool:
    """Function that verifies whether a string complies with the spanish phone number nomenclature."""
    phone_number = number.replace(" ", "")

    # ^ regex start
    # \+? 1 or 0 '+' 
    # \d{9,15} 9 a 15 digits
    return bool(re.match(r"^\+?\d{9,15}$", phone_number))
        