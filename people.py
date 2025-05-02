class Person:
    def __init__(self, name, number, home_address):
        self.name = name
        self.number = number
        self.home_address = home_address


class GosPerson(Person):
    def __init__(self, name, number):
        self.name = name
        self.number = number