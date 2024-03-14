def random_username(country: str, email: str = None, phone: str = None, is_organization: bool = False):
    username = "user_{}_".format(country) if is_organization is False else "partner_{}_".format(country)

    if email is not None:
        username += email
    if phone is not None:
        username += str(phone)

    return username
