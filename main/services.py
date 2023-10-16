import random


def random_choice(clients: list) -> list:
    result_list = []

    if len(clients) >= 3:
        result_list = random.choices(clients, k=3)
        return result_list
    elif len(clients) == 2:
        result_list = random.choices(clients, k=2)
        return result_list
    elif len(clients) == 1:
        result_list = random.choices(clients, k=1)
        return result_list
    else:
        return result_list
