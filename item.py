class Item:
    def __init__(self, name):
        self.name = name

    def calculate_cost(self):
        pass


class Gold(Item):
    def __init__(self, name, weight, proba):
        self.name = name
        self.weight = weight
        self.proba = proba
        self.estimation = self.calculate_cost()

    def calculate_cost(self):
        if 750 < self.proba <= 1000:
            return self.weight * 7000
        elif 700 < self.proba <= 750:
            return self.weight * 4928
        elif 600 < self.proba <= 700:
            return self.weight * 4005
        elif 500 < self.proba <= 600:
            return self.proba * 3245
        elif 400 < self.proba <= 500:
            return self.weight * 2756
        else:
            return self.weight * 2020


class Fur(Item):
    def __init__(self, name, weight, cost_fur, degree_wear):
        self.name = name
        self.weight = weight
        self.cost_fur = cost_fur
        self.degree_wear = degree_wear
        self.estimation = self.calculate_cost()

    def calculate_cost(self):
        return self.weight * self.cost_fur * ((100 - self.degree_wear) / 100)


class Appliance(Item):
    def __init__(self, name, time_usage, cost_new_analog):
        self.name = name
        self.time_usage = time_usage
        self.cost_new_analog = cost_new_analog
        self.estimation = self.calculate_cost()

    def calculate_cost(self):
        if self.time_usage > 6:
            return self.cost_new_analog * 0.2
        elif 4 <= self.time_usage <= 6:
            return self.cost_new_analog * 0.5
        elif 2 <= self.time_usage < 4:
            return self.cost_new_analog * 0.7
        else:
            return self.cost_new_analog
