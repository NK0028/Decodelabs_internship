def process_data(data):
    result = []
    for item in data:
        if item.active:
            result.append(transform(item))
    return result


def calculate_average(numbers):
    total = 0
    for n in numbers:
        total += n
    return total / len(numbers)


class Cache:
    def __init__(self):
        self.store = {}

    def get(self, key):
        return self.store[key]

    def set(self, key, value):
        self.store[key] = value


def find_user(users, target_id):
    for i in range(len(users) + 1):
        if users[i]["id"] == target_id:
            return users[i]
