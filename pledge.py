class Pledge:
    def __init__(self, person, items, loan_term, cur_day=1):
        self.person = person
        self.items = items
        self.loan = sum(item.estimation * 0.5 for item in self.items)
        self.loan_proc = self.loan
        self.loan_term = loan_term
        self.end_day = loan_term + cur_day
        self.delayed = False
        self.overdue_days = 0
        self.cnt_pay = 0
        self.shtraf = 0
        self.proc = 0
        self.payments = self.calculate_payments(cur_day + loan_term, cur_day)

    def calculate_payments(self, end_day, cur_day=1):
        if end_day - cur_day == 15:
            interval = 5
            total_pay = 3
            self.shtraf = 0.04
            self.proc = 0.01
        elif end_day - cur_day == 30:
            interval = 6
            total_pay = 5
            self.shtraf = 0.05
            self.proc = 0.02
        elif end_day - cur_day == 45:
            interval = 9
            total_pay = 5
            self.shtraf = 0.055
            self.proc = 0.025
        elif end_day - cur_day == 60:
            interval = 10
            total_pay = 6
            self.shtraf = 0.06
            self.proc = 0.03

        self.cnt_pay = total_pay
        pay_amount = self.loan / total_pay
        return [{'day': i * interval + cur_day, 'amount': pay_amount, 'paid': False, 'active': False} for i in
                range(1, total_pay + 1)]
