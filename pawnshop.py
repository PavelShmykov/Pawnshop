from pledge import *
from item import *
from people import *
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox
from tksheet import Sheet
from random import choice, randint
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import csv


class Pawnshop:
    def __init__(self):
        self.pledges = self.read_pledges_from_csv('Ломбард начальные.csv')
        self.random_pledges = self.read_pledges_from_csv('Ломбард рандомные.csv')
        self.current_day = 1
        self.delayed_pledges = []
        self.sold_items = []
        self.pending_sold_items = []
        self.income_by_type = {"Золото": 0, "Меха": 0, "Бытовая техника": 0}
        self.planned_income = 0

        self.start_date = datetime(2025, 1, 1)
        self.formatted_date = self.start_date.strftime('%d.%m.%Y')
        self.income_each_day = {1: 0}
        self.expenses_each_day = {1: sum(i.loan for i in self.pledges)}

        self.window = tk.Tk()
        self.window.title('Ломбард')
        self.window.geometry("830x540")
        self.window.resizable(False, False)
        self.window.configure(bg="#f5f5f5")

    def reload(self):
        [child.destroy() for child in self.window.winfo_children()]
        self.window.destroy()
        self.__init__()
        self.create_widgets()

    def create_widgets(self):
        head = tk.Label(
            self.window,
            text="Добро пожаловать в Ломбард «Не забудь забрать»!",
            font=("Arial", 20, 'bold'),
            bg="#f5f5f5",
            fg="#333"
        )
        head.grid(row=0, column=0, columnspan=2, pady=10, sticky="nsew")

        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)

        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label='Перезагрузить', command=self.reload)
        settings_menu.add_command(label='Выход', command=self.window.destroy)
        menubar.add_cascade(label='Файл', menu=settings_menu)

        self.day_label = tk.Label(
            self.window,
            text=f"Дата: {self.formatted_date}",
            font=("Arial", 16),
            bg="#f5f5f5",
            fg="#333",
            anchor="w"
        )
        self.day_label.grid(row=1, column=0, pady=5, padx=10, sticky="w")

        planned_income_frame = tk.Frame(self.window, bg="#f5f5f5")
        planned_income_label = tk.Label(
            planned_income_frame,
            text="Планируемый доход за сегодня: ",
            font=("Arial", 14),
            bg="#f5f5f5",
            fg="#333"
        )
        planned_income_label.pack(side="left")
        self.planned_income_label = tk.Label(
            planned_income_frame,
            text=f"{self.planned_income} руб.",
            font=("Arial", 14, 'bold'),
            bg="#f5f5f5",
            fg="#4CAF50"
        )
        self.planned_income_label.pack(side="left")
        planned_income_frame.grid(row=2, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")

        self.window.grid_rowconfigure(3, weight=0)
        self.window.grid_columnconfigure(0, weight=0)
        self.window.grid_columnconfigure(1, weight=0)

        self.pledge_frame = tk.Frame(
            self.window, bg="#f5f5f5", bd=2, relief="groove", width=1100, height=400)
        self.pledge_frame.grid(row=3, column=0, sticky="nw", padx=10, pady=10)

        pledge_label = tk.Label(
            self.pledge_frame,
            text="Список залогов",
            font=("Arial", 14, 'bold'),
            bg="#f5f5f5"
        )
        pledge_label.pack(pady=5)

        self.pledge_sheet = Sheet(
            self.pledge_frame,
            headers=["Имя", "Сумма долга", "Выплата"], empty_horizontal=False, empty_vertical=False
        )
        self.pledge_sheet.pack(fill="both", expand=True, padx=5, pady=5)
        self.pledge_sheet.default_row_height(40)
        self.pledge_sheet.default_column_width(126)

        self.button_frame = tk.Frame(self.window, bg="#f5f5f5", bd=2, relief="groove", width=300, height=400)
        self.button_frame.grid(row=3, column=1, sticky="nw", padx=10, pady=10)
        self.button_frame.grid_propagate(False)

        buttons = [
            {"text": "Следующий день", "command": self.next_day},
            {"text": "Действия с залогами", "command": self.pledge_action_window},
            {"text": "Добавить залог", "command": self.show_add_pledge_window},
            {"text": "Сумма доходов и расходов за каждый день", "command": self.show_income_expense_chart},
            {"text": "Просроченные залоги", "command": self.show_delayed_pledges},
            {"text": "Люди, задерживающие выплаты", "command": self.show_delayed_payments_window},
            {"text": "Распределить доходы", "command": self.show_income_distribution},
            {"text": "Проданные вещи", "command": self.show_sold_items_window},
        ]

        for btn in buttons:
            button = tk.Button(
                self.button_frame,
                text=btn["text"],
                command=btn["command"],
                font=("Arial", 12),
                bg="#4CAF50",
                fg="white",
                activebackground="#45a049",
                relief="raised",
                bd=3
            )
            button.pack(fill="x", expand=True, pady=5, padx=5)
            self.add_hover_effect(button)

        self.update_pledges()

    @staticmethod
    def add_hover_effect(button):
        def on_enter(event):
            button.config(fg="black")
        def on_leave(event):
            button.config(fg="white")
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def update_pledges(self):
        data = []
        for pledge in self.pledges:
            status = "Не активна"
            for pay in pledge.payments:
                if (not pay['paid']) and (pay['day'] <= self.current_day):
                    status = "Активна"
                    break
            data.append([
                pledge.person.name,
                f"{pledge.loan:.2f} руб.",
                status
            ])

        self.pledge_sheet.set_sheet_data(data)

        for i, row in enumerate(data):
            self.pledge_sheet.highlight_rows(
                rows=[i],
                bg="#ffffff",
                fg="#000000",
            )

            status = row[2]
            status_color = "#4CAF50" if status == "Активна" else "#FF0000"
            self.pledge_sheet.highlight_cells(
                row=i,
                column=2,
                bg="#ffffff",
                fg=status_color,
            )

        self.planned_income_label.config(text=f"{self.planned_income:.2f} руб.")

    def next_day(self):
        if self.income_each_day[self.current_day] == 0:
            pledge = choice([self.pledges[6], self.pledges[8], self.pledges[10]])
            self.update_income_by_type(pledge, pledge.loan)
            self.income_each_day[self.current_day] += pledge.loan
            self.pledges.remove(pledge)
            self.update_pledges()


        current_date = self.start_date + timedelta(days=self.current_day)
        self.formatted_date = current_date.strftime('%d.%m.%Y')
        self.day_label.config(text=f"Дата: {self.formatted_date}")
        self.current_day += 1

        self.income_each_day[self.current_day] = 0
        self.expenses_each_day[self.current_day] = 0

        self.calculate_planned_income()

        for pledge in self.pledges[:]:
            daily_interest = pledge.loan_proc * pledge.proc
            pledge.loan += daily_interest

            if self.current_day > pledge.end_day:
                pledge.delayed = True
                pledge.overdue_days = self.current_day - pledge.end_day

                if pledge.overdue_days > 30 and pledge not in self.pending_sold_items:
                    self.pending_sold_items.append(pledge)
                    self.sold_items.extend(pledge.items)
                    self.pledges.remove(pledge)
                    continue

                if pledge.overdue_days <= 30:
                    penalty = pledge.overdue_days * pledge.shtraf * pledge.loan_proc
                    pledge.loan += penalty

            for payment in pledge.payments:
                if payment["day"] < self.current_day and not payment["paid"]:
                    penalty = pledge.shtraf * pledge.loan_proc
                    pledge.loan += penalty
                    break

        for i in range(randint(1, 2)):
            pledge = choice(self.random_pledges)
            pledge.start_day = self.current_day
            pledge.end_day = pledge.start_day + pledge.loan_term
            pledge.delayed = False
            pledge.overdue_days = 0
            pledge.payments = pledge.calculate_payments(pledge.start_day + pledge.loan_term, pledge.start_day)
            self.pledges.append(pledge)
            self.update_pledges()
            self.expenses_each_day[self.current_day] += pledge.loan

        if hasattr(self, 'pay_list_updater') and callable(self.pay_list_updater):
            try:
                self.pay_list_updater()
            except Exception as e:
                self.pay_list_updater = None

        self.update_pledges()
        self.update_pending_sold_items()

    def calculate_planned_income(self):
        self.planned_income = 0
        for pledge in self.pledges:
            for payment in pledge.payments:
                if payment["day"] == self.current_day and not payment["paid"]:
                    self.planned_income += payment["amount"]

    def update_pending_sold_items(self):
        for pledge in self.pending_sold_items[:]:
            if self.current_day >= pledge.end_day + 90:
                self.income_each_day[self.current_day] += sum(item.estimation for item in pledge.items) * 2
                self.pending_sold_items.remove(pledge)

    def pledge_action_window(self):
        action_window = tk.Toplevel(self.window)
        action_window.title("Действие с залогами")
        action_window.geometry("300x170")
        action_window.configure(bg="#f5f5f5")
        action_window.resizable(False, False)

        repay_button = tk.Button(
            action_window,
            text="Погасить залог",
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            command=self.show_repay_window
        )
        repay_button.pack(fill="x", padx=10, pady=5)
        self.add_hover_effect(repay_button)

        payment_button = tk.Button(
            action_window,
            text="Внести оплату",
            font=("Arial", 12),
            bg="#FFA500",
            fg="white",
            activebackground="#FF8C00",
            command=self.show_pay_window
        )
        payment_button.pack(fill="x", padx=10, pady=5)
        self.add_hover_effect(payment_button)

        restart_pledge_button = tk.Button(
            action_window,
            text="Продлить залог",
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            command=self.show_continue_window
        )
        restart_pledge_button.pack(fill="x", padx=10, pady=5)
        self.add_hover_effect(restart_pledge_button)

        condition_pledge_button = tk.Button(
            action_window,
            text="Состояние залога",
            font=("Arial", 12),
            bg="#FFA500",
            fg="white",
            activebackground="#FF8C00",
            command=self.show_condition_window
        )
        condition_pledge_button.pack(fill="x", padx=10, pady=5)
        self.add_hover_effect(condition_pledge_button)

    def show_repay_window(self):
        repay_window = tk.Toplevel(self.window)
        repay_window.title("Погашение залогов")
        repay_window.geometry("430x300")
        repay_window.configure(bg="#f5f5f5")
        repay_window.resizable(True, False)
        repay_window.wm_maxsize(450, 300)

        header_label = tk.Label(
            repay_window,
            text="Список залогов для погашения", font=("Arial", 14, 'bold'), bg="#4CAF50", fg="white")
        header_label.grid(row=0, column=0, columnspan=2, pady=10, sticky='we')

        canvas = tk.Canvas(repay_window, bg="#f5f5f5")
        canvas.grid(row=1, column=0, sticky="nsew")

        scrollbar = tk.Scrollbar(repay_window, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollable_frame = tk.Frame(canvas, bg="#f5f5f5")
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def update_repay_list():
            for widget in scrollable_frame.winfo_children():
                widget.destroy()

            for i, pledge in enumerate(self.pledges, start=1):
                pledge_label = tk.Label(
                    scrollable_frame,
                    text=f"Залог {i}: {pledge.person.name} - {pledge.loan:.2f} руб.",
                    font=("Arial", 12),
                    bg="#f5f5f5",
                    anchor="w"
                )
                pledge_label.grid(row=i, column=0, sticky="w", padx=10, pady=2)

                repay_button = tk.Button(
                    scrollable_frame,
                    text="Погасить залог",
                    font=("Arial", 10),
                    bg="#4CAF50",
                    fg="white",
                    activebackground="#45a049",
                    command=lambda p=pledge: repay_pledge(p)
                )
                repay_button.grid(row=i, column=1, sticky="e", padx=10, pady=2)
                self.add_hover_effect(repay_button)

        def repay_pledge(pledge):
            self.pay_all_pledge(pledge)
            update_repay_list()

        update_repay_list()

        repay_window.grid_rowconfigure(1, weight=1)
        repay_window.grid_columnconfigure(0, weight=1)

    def pay_all_pledge(self, pledge: Pledge):
        self.update_income_by_type(pledge, pledge.loan)
        self.income_each_day[self.current_day] += pledge.loan
        print(f"{pledge.person.name} погасил долг")
        self.pledges.remove(pledge)
        self.update_pledges()



    def show_pay_window(self):
        repay_window = tk.Toplevel(self.window)
        repay_window.title("Выплаты за залоги")
        repay_window.geometry("430x300")
        repay_window.configure(bg="#f5f5f5")
        repay_window.resizable(True, False)
        repay_window.wm_maxsize(450, 300)

        header_label = tk.Label(
            repay_window,
            text="Список залогов", font=("Arial", 14, 'bold'), bg="#4CAF50", fg="white")
        header_label.grid(row=0, column=0, columnspan=2, pady=10, sticky='we')

        canvas = tk.Canvas(repay_window, bg="#f5f5f5")
        canvas.grid(row=1, column=0, sticky="nsew")

        scrollbar = tk.Scrollbar(repay_window, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollable_frame = tk.Frame(canvas, bg="#f5f5f5")
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def update_pay_list():
            for widget in scrollable_frame.winfo_children():
                widget.destroy()

            for i, pledge in enumerate(self.pledges, start=1):
                pledge_label = tk.Label(
                    scrollable_frame,
                    text=f"Залог {i}: {pledge.person.name} - {pledge.loan:.2f} руб.",
                    font=("Arial", 12),
                    bg="#f5f5f5",
                    anchor="w"
                )
                pledge_label.grid(row=i, column=0, sticky="w", padx=10, pady=2)

                payment_status = any(
                    (payment["day"] <= self.current_day and not payment["paid"]) for payment in pledge.payments
                )

                repay_button = tk.Button(
                    scrollable_frame,
                    text="Внести плату",
                    font=("Arial", 10),
                    bg="#FFA500",
                    fg="white",
                    activebackground="#FF8C00",
                    state="normal" if payment_status else "disabled",
                    command=lambda p=pledge: pay_pledge(p)
                )
                repay_button.grid(row=i, column=1, sticky="e", padx=10, pady=2)
                self.add_hover_effect(repay_button)

        def pay_pledge(pledge):
            self.make_pay(pledge)
            update_pay_list()

        self.pay_list_updater = update_pay_list

        update_pay_list()

        repay_window.grid_rowconfigure(1, weight=1)
        repay_window.grid_columnconfigure(0, weight=1)

    def make_pay(self, pledge: Pledge):
        total_payment = 0
        overdue_days_total = 0
        overdue_penalty_total = 0

        for payment in pledge.payments:
            if payment["day"] <= self.current_day and pledge.cnt_pay == 1:

                total_payment = pledge.loan
                pledge.loan = 0
                payment["paid"] = True
                payment["active"] = False
                pledge.cnt_pay -= 1
                self.pledges.remove(pledge)

            if payment["day"] <= self.current_day and not payment["paid"]:
                overdue_days = self.current_day - payment["day"] if self.current_day > payment["day"] else 0
                overdue_penalty = overdue_days * pledge.shtraf * pledge.loan_proc
                interest = overdue_days * pledge.proc * pledge.loan_proc

                overdue_days_total += overdue_days
                overdue_penalty_total += overdue_penalty
                total_payment += payment["amount"] + overdue_penalty + interest

                payment["paid"] = True
                payment["active"] = False
                pledge.cnt_pay -= 1
                print(pledge.cnt_pay)

                pledge.loan -= payment["amount"]

        self.update_income_by_type(pledge, total_payment)
        self.income_each_day[self.current_day] += total_payment
        self.update_pledges()

    def show_continue_window(self):
        repay_window = tk.Toplevel(self.window)
        repay_window.title("Продление залогов")
        repay_window.geometry("430x300")
        repay_window.configure(bg="#f5f5f5")
        repay_window.resizable(True, False)

        header_label = tk.Label(
            repay_window,
            text="Список залогов для погашения", font=("Arial", 14, 'bold'), bg="#4CAF50", fg="white")
        header_label.grid(row=0, column=0, columnspan=2, pady=10, sticky='we')

        canvas = tk.Canvas(repay_window, bg="#f5f5f5")
        canvas.grid(row=1, column=0, sticky="nsew")

        scrollbar = tk.Scrollbar(repay_window, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollable_frame = tk.Frame(canvas, bg="#f5f5f5")
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def update_cont_list():
            for widget in scrollable_frame.winfo_children():
                widget.destroy()

            for i, pledge in enumerate(self.pledges, start=1):
                pledge_label = tk.Label(
                    scrollable_frame,
                    text=f"Залог {i}: {pledge.person.name} - {pledge.loan:.2f} руб.",
                    font=("Arial", 12),
                    bg="#f5f5f5",
                    anchor="w"
                )
                pledge_label.grid(row=i, column=0, sticky="w", padx=10, pady=2)

                contin_button = tk.Button(
                    scrollable_frame,
                    text="Продлить залоги",
                    font=("Arial", 10),
                    bg="#4CAF50",
                    fg="white",
                    activebackground="#45a049",
                    command=lambda p=pledge: con_pledge(p)
                )
                contin_button.grid(row=i, column=1, sticky="e", padx=10, pady=2)
                self.add_hover_effect(contin_button)

        def con_pledge(pledge):
            self.continue_pledge(pledge)

        update_cont_list()
        self.cont_list_updater = update_cont_list

        repay_window.grid_rowconfigure(1, weight=1)
        repay_window.grid_columnconfigure(0, weight=1)

    def continue_pledge(self, pledge):
        continue_window = tk.Toplevel(self.window)
        continue_window.title("Продлить залог")
        continue_window.geometry("350x250")
        continue_window.config(bg="#f5f5f5")
        continue_window.resizable(False, False)

        tk.Label(continue_window, text="Выберите срок продления займа (дней):", font=("Arial", 12, 'bold'), bg="#4CAF50", fg="white").pack(pady=5, fill="x")

        loan_term_var = tk.IntVar(value=15)

        for days in [15, 30, 45, 60]:
            tk.Radiobutton(continue_window, text=f"{days} дней", variable=loan_term_var, value=days,
                           font=("Arial", 12), bg="#f5f5f5").pack(anchor="w", padx=20)

        def save_pledge():
            procent = pledge.loan - pledge.loan_proc
            self.update_income_by_type(pledge, procent)
            self.income_each_day[self.current_day] += procent
            additional_days = loan_term_var.get()
            new_pledge = Pledge(
                person=pledge.person,
                items=pledge.items,
                loan_term=additional_days
            )
            self.pledges.append(new_pledge)
            self.pledges.remove(pledge)
            self.update_pledges()
            continue_window.destroy()
            self.cont_list_updater()


        button = tk.Button(continue_window, text="Продлить", font=("Arial", 12), bg="#4CAF50", fg="white", command=save_pledge)
        button.pack(pady=10)
        self.add_hover_effect(button)


    def show_condition_window(self):
        repay_window = tk.Toplevel(self.window)
        repay_window.title("Состояние залогов")
        repay_window.geometry("440x300")
        repay_window.configure(bg="#f5f5f5")
        repay_window.resizable(False, False)

        header_label = tk.Label(
            repay_window,
            text="Список залогов", font=("Arial", 14, 'bold'), bg="#4CAF50", fg="white")
        header_label.grid(row=0, column=0, columnspan=2, pady=10, sticky='we')

        canvas = tk.Canvas(repay_window, bg="#f5f5f5")
        canvas.grid(row=1, column=0, sticky="nsew")

        scrollbar = tk.Scrollbar(repay_window, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollable_frame = tk.Frame(canvas, bg="#f5f5f5")
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def update_repay_list():
            for widget in scrollable_frame.winfo_children():
                widget.destroy()

            for i, pledge in enumerate(self.pledges, start=1):
                pledge_label = tk.Label(
                    scrollable_frame,
                    text=f"Залог {i}: {pledge.person.name} - {pledge.loan:.2f} руб.",
                    font=("Arial", 12),
                    bg="#f5f5f5",
                    anchor="w"
                )
                pledge_label.grid(row=i, column=0, sticky="w", padx=10, pady=2)

                repay_button = tk.Button(
                    scrollable_frame,
                    text="Состояние залога",
                    font=("Arial", 10),
                    bg="#4CAF50",
                    fg="white",
                    activebackground="#45a049",
                    command=lambda p=pledge: condition_pledge(p)
                )
                repay_button.grid(row=i, column=1, sticky="e", padx=10, pady=2)
                self.add_hover_effect(repay_button)

        def condition_pledge(pledge):
            self.show_pledge_condition(pledge)

        update_repay_list()

        repay_window.grid_rowconfigure(1, weight=1)
        repay_window.grid_columnconfigure(0, weight=1)

    def show_pledge_condition(self, pledge):
        condition_window = tk.Toplevel(self.window)
        condition_window.title("Состояние залога")
        condition_window.geometry("600x400")
        condition_window.resizable(False, False)
        condition_window.config(bg="#f5f5f5")

        tk.Label(condition_window, text="Состояние залога", font=("Arial", 16, "bold"), bg="#4CAF50", fg="white").pack(
            fill="x", pady=10)

        canvas_frame = tk.Frame(condition_window, bg="#f5f5f5")
        canvas_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(canvas_frame, bg="#f5f5f5", highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.config(yscrollcommand=scrollbar.set)

        content_frame = tk.Frame(canvas, bg="#f5f5f5")
        canvas.create_window((0, 0), window=content_frame, anchor="nw")

        client_frame = tk.Frame(content_frame, bg="#f5f5f5")
        client_frame.pack(fill="x", pady=5, padx=10)

        tk.Label(client_frame, text="Имя клиента:", font=("Arial", 12), bg="#f5f5f5").grid(row=0, column=0, sticky="w",
                                                                                           padx=5)
        tk.Label(client_frame, text=pledge.person.name, font=("Arial", 12, "bold"), bg="#f5f5f5").grid(row=0, column=1,
                                                                                                       sticky="w",
                                                                                                       padx=5)

        tk.Label(client_frame, text="Тип клиента:", font=("Arial", 12), bg="#f5f5f5").grid(row=1, column=0, sticky="w",
                                                                                           padx=5)
        person_type = "Госслужащий" if isinstance(pledge.person, GosPerson) else "Обычный клиент"
        tk.Label(client_frame, text=person_type, font=("Arial", 12, "bold"), bg="#f5f5f5").grid(row=1, column=1,
                                                                                                sticky="w", padx=5)

        tk.Label(client_frame, text="Номер документа:", font=("Arial", 12), bg="#f5f5f5").grid(row=2, column=0,
                                                                                               sticky="w", padx=5)
        tk.Label(client_frame, text=getattr(pledge.person, 'passport', getattr(pledge.person, 'number', 'Нет данных')),
                 font=("Arial", 12, "bold"), bg="#f5f5f5").grid(row=2, column=1, sticky="w", padx=5)

        # Add address for Person class
        if isinstance(pledge.person, Person) and not isinstance(pledge.person, GosPerson):
            tk.Label(client_frame, text="Адрес клиента:", font=("Arial", 12), bg="#f5f5f5").grid(row=3, column=0,
                                                                                                 sticky="w", padx=5)
            tk.Label(client_frame, text=pledge.person.home_address, font=("Arial", 12, "bold"), bg="#f5f5f5").grid(
                row=3, column=1, sticky="w", padx=5)

        finance_frame = tk.Frame(content_frame, bg="#f5f5f5")
        finance_frame.pack(fill="x", pady=5, padx=10)

        tk.Label(finance_frame, text="Сумма долга:", font=("Arial", 12), bg="#f5f5f5").grid(row=0, column=0, sticky="w",
                                                                                            padx=5)
        tk.Label(finance_frame, text=f"{pledge.loan:.2f} руб.", font=("Arial", 12, "bold"), bg="#f5f5f5").grid(row=0,
                                                                                                               column=1,
                                                                                                               sticky="w",
                                                                                                               padx=5)

        tk.Label(finance_frame, text="Срок залога:", font=("Arial", 12), bg="#f5f5f5").grid(row=1, column=0, sticky="w",
                                                                                            padx=5)
        tk.Label(finance_frame, text=f"{pledge.loan_term} дней", font=("Arial", 12, "bold"), bg="#f5f5f5").grid(row=1,
                                                                                                                column=1,
                                                                                                                sticky="w",
                                                                                                                padx=5)

        tk.Label(finance_frame, text="Проценты:", font=("Arial", 12), bg="#f5f5f5").grid(row=2, column=0, sticky="w",
                                                                                         padx=5)
        tk.Label(finance_frame, text=f"{pledge.proc * 100} % / день", font=("Arial", 12, "bold"), bg="#f5f5f5",
                 fg='green').grid(row=2, column=1, sticky="w", padx=5)

        tk.Label(finance_frame, text="Штрафы:", font=("Arial", 12), bg="#f5f5f5").grid(row=3, column=0, sticky="w",
                                                                                       padx=5)
        tk.Label(finance_frame, text=f"{pledge.shtraf * 100} % / день", font=("Arial", 12, "bold"), bg="#f5f5f5",
                 fg='red').grid(row=3, column=1, sticky="w", padx=5)

        tk.Label(finance_frame, text="Статус залога:", font=("Arial", 12), bg="#f5f5f5").grid(row=4, column=0,
                                                                                              sticky="w", padx=5)
        status = "Активен" if not pledge.delayed else "Просрочен"
        tk.Label(finance_frame, text=status, font=("Arial", 12, "bold"), bg="#f5f5f5",
                 fg="red" if pledge.delayed else "green").grid(row=4, column=1, sticky="w", padx=5)

        items_frame = tk.Frame(content_frame, bg="#f5f5f5")
        items_frame.pack(fill="x", pady=5, padx=10)

        tk.Label(items_frame, text="Вещи в залоге:", font=("Arial", 12, "bold"), bg="#f5f5f5").pack(anchor="w", padx=5)

        for item in pledge.items:
            tk.Label(items_frame, text=f"- {item.name}", font=("Arial", 12), bg="#f5f5f5").pack(anchor="w", padx=20)

        content_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def update_income_by_type(self, pledge: Pledge, amount):
        for item in pledge.items:
            item_share = round((item.estimation / pledge.loan_proc) * amount * 0.5, 2)
            if isinstance(item, Gold):
                self.income_by_type["Золото"] += item_share
            elif isinstance(item, Fur):
                self.income_by_type['Меха'] += item_share
            elif isinstance(item, Appliance):
                self.income_by_type["Бытовая техника"] += item_share

    def show_income_distribution(self):
        distribution_window = tk.Toplevel(self.window)
        distribution_window.title("Распределение доходов по типам вещей")
        distribution_window.geometry("450x350")
        distribution_window.config(bg="#f5f5f5")
        distribution_window.resizable(False, False)

        tk.Label(
            distribution_window,
            text="Распределение доходов",
            font=("Arial", 18, "bold"),
            bg="#4CAF50",
            fg="white"
        ).pack(fill="x", pady=15)

        content_frame = tk.Frame(distribution_window, bg="#ffffff", bd=2, relief="groove")
        content_frame.pack(fill="both", padx=20, pady=10)

        tk.Label(
            content_frame,
            text="Доходы по категориям:",
            font=("Arial", 14, "bold"),
            bg="#ffffff",
            fg="#333"
        ).pack(anchor="w", padx=10, pady=10)

        colors = {"Золото": "#FFD700", "Меха": "#8B4513", "Бытовая техника": "#4682B4"}

        for type_name, income in self.income_by_type.items():
            tk.Frame(content_frame, bg=colors[type_name], height=2).pack(fill="x", pady=5, padx=20)
            tk.Label(content_frame, text=f"{type_name}: {income:.2f} руб.", font=("Arial", 12, "bold"),
                     bg="#ffffff", fg="#333").pack(anchor="w", padx=20, pady=5)


    def show_delayed_payments_window(self):
        window = tk.Toplevel(self.window)
        window.title("Просроченные выплаты")
        window.geometry("500x300")
        window.resizable(False, False)
        window.resizable(False, False)
        window.config(bg="#f5f5f5")

        tk.Label(window, text="Введите количество задержек", font=("Arial", 16, "bold"),
                 bg="#4CAF50", fg="white", pady=10).pack(pady=10, fill="x")

        delay_frame = tk.Frame(window, bg="#f5f5f5")
        delay_frame.pack(pady=10)
        tk.Label(delay_frame, text="Количество задержек:", font=("Arial", 14), bg="#f5f5f5").pack(side="left", padx=10)
        delay_input = tk.Entry(delay_frame, font=("Arial", 14), bg="#fff", fg="#333", width=10)
        delay_input.pack(side="left", padx=10)

        def process_threshold():
            for widget in window.pack_slaves():
                if isinstance(widget, tk.Label) and "Ошибка" in widget.cget("text"):
                    widget.destroy()

            try:
                threshold = int(delay_input.get())
                delayed_people = self.get_people_with_delayed_payments(threshold)

                result_window = tk.Toplevel(self.window)
                result_window.title("Результаты просрочек")
                result_window.geometry("700x450")
                result_window.resizable(False, False)
                result_window.config(bg="#f5f5f5")

                tk.Label(result_window, text=f"Люди с задержками больше {threshold} раз:", font=("Arial", 18, "bold"),
                         bg="#4CAF50", fg="white", pady=10).pack(pady=10, fill="x")

                if not delayed_people:
                    tk.Label(result_window, text="Нет людей с задержками выплат.", font=("Arial", 16, "bold"),
                             bg="#f5f5f5", fg="red").pack(pady=20)
                else:
                    sheet_frame = tk.Frame(result_window, bg="#f5f5f5")
                    sheet_frame.pack(fill="both", expand=True, padx=10, pady=10)

                    sheet = Sheet(sheet_frame, headers=["Имя клиента", "Номер документа", "Количество задержек"],
                                  empty_horizontal=False, empty_vertical=False)

                    data = [[person['name'], person['passport'], f"{person['delayed_count']} раз(-а)"] for person in
                            delayed_people]
                    sheet.set_sheet_data(data)

                    sheet.column_width(0, 200)
                    sheet.column_width(1, 200)
                    sheet.column_width(2, 250)

                    sheet.pack(fill="both", expand=True)

            except ValueError:
                messagebox.showerror("Ошибка ввода", "Пожалуйста, введите числовое значение.")

        button = tk.Button(window, text="Показать результаты", font=("Arial", 12), bg="#4CAF50", fg="white",
                  activebackground="#45a049", command=process_threshold)
        button.pack(pady=20)
        self.add_hover_effect(button)

    def get_people_with_delayed_payments(self, threshold):
        delayed_people = []
        for pledge in self.pledges:
            delayed_count = 0
            for payment in pledge.payments:
                if payment["day"] < self.current_day and payment["paid"]:
                    delayed_count += 1
            if delayed_count > threshold:
                person_info = {
                    "name": pledge.person.name,
                    "passport": pledge.person.number,
                    "delayed_count": delayed_count
                }
                delayed_people.append(person_info)
        print(f"Отладка задержек: {delayed_people}")
        return delayed_people

    def show_delayed_pledges(self):
        delayed_window = tk.Toplevel(self.window)
        delayed_window.title("Просроченные залоги")
        delayed_window.geometry("800x600")
        delayed_window.resizable(False, False)
        delayed_window.config(bg="#f5f5f5")

        tk.Label(delayed_window, text="Просроченные залоги", font=("Arial", 14, "bold"), bg="#4CAF50", fg="white").pack(
            pady=10, fill='x')

        sort_frame = tk.Frame(delayed_window, bg="#f5f5f5")
        sort_frame.pack(pady=10)
        tk.Label(sort_frame, text="Сортировать по:", font=("Arial", 12), bg="#f5f5f5").pack(side="left", padx=5)

        sort_options = ["Дней просрочки", "Сумма долга", "Имя клиента"]
        sort_var = tk.StringVar(value=sort_options[0])

        sort_menu = tk.OptionMenu(sort_frame, sort_var, *sort_options, command=lambda _: update_table())
        sort_menu.config(font=("Arial", 12), bg="#4CAF50", fg="white", activebackground="#45a049", width=15)
        sort_menu.pack(side="left", padx=5)

        table_frame = tk.Frame(delayed_window, bg="#f5f5f5")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        def update_table():
            for widget in table_frame.winfo_children():
                widget.destroy()

            key_map = {
                "Дней просрочки": lambda x: x.overdue_days,
                "Сумма долга": lambda x: x.loan,
                "Имя клиента": lambda x: x.person.name.lower(),
            }
            sort_key = key_map[sort_var.get()]
            reverse = sort_var.get() != 'Имя клиента'

            delayed_pledges = sorted(
                [pledge for pledge in self.pledges if pledge.delayed],
                key=sort_key,
                reverse=reverse
            )

            sheet = Sheet(
                table_frame,
                headers=["Имя клиента", "Дней просрочки", "Сумма долга", "Номер документа"],
                empty_horizontal=False,
                empty_vertical=False
            )

            data = [
                [pledge.person.name, pledge.overdue_days, f"{pledge.loan:.2f} руб.", pledge.person.number]
                for pledge in delayed_pledges
            ]
            sheet.set_sheet_data(data)

            sheet.column_width(0, 200)
            sheet.column_width(1, 150)
            sheet.column_width(2, 200)
            sheet.column_width(3, 200)

            sheet.pack(fill="both", expand=True)

        update_table()

    def show_sold_items_window(self):
        sold_items_window = tk.Toplevel(self.window)
        sold_items_window.title("Проданные вещи")
        sold_items_window.geometry("560x600")
        sold_items_window.resizable(False, False)
        sold_items_window.config(bg="#f5f5f5")

        tk.Label(sold_items_window, text="Проданные вещи", font=("Arial", 14, "bold"), bg="#4CAF50", fg="white").pack(
            pady=10, fill='x')

        sort_frame = tk.Frame(sold_items_window, bg="#f5f5f5")
        sort_frame.pack(pady=10)
        tk.Label(sort_frame, text="Сортировать по:", font=("Arial", 12), bg="#f5f5f5").pack(side="left", padx=5)

        sort_options = ["Наименование", "Тип"]
        sort_var = tk.StringVar(value=sort_options[0])

        sort_menu = tk.OptionMenu(sort_frame, sort_var, *sort_options, command=lambda _: update_table())
        sort_menu.config(font=("Arial", 12), bg="#4CAF50", fg="white", activebackground="#45a049", width=15)
        sort_menu.pack(side="left", padx=5)

        table_frame = tk.Frame(sold_items_window, bg="#f5f5f5")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        current_sheet = None

        def update_table():
            nonlocal current_sheet

            if current_sheet:
                current_sheet.destroy()

            key_map = {
                "Наименование": lambda x: x.name.lower(),
                "Тип": lambda x: "Золото" if isinstance(x, Gold) else "Меха" if isinstance(x,
                                                                                           Fur) else "Бытовая техника",
            }
            sort_key = key_map[sort_var.get()]
            sorted_sold_items = sorted(self.sold_items, key=sort_key)

            data = [
                [
                    item.name,
                    f"{item.estimation:.2f} руб.",
                    "Золото" if isinstance(item, Gold) else "Меха" if isinstance(item, Fur) else "Бытовая техника"
                ]
                for item in sorted_sold_items
            ]

            current_sheet = Sheet(
                table_frame,
                headers=["Наименование", "Стоимость", "Тип"],
                data=data,
                empty_horizontal=False,
                empty_vertical=False
            )
            current_sheet.pack(fill="both", expand=True)

            current_sheet.column_width(0, 200)
            current_sheet.column_width(1, 150)
            current_sheet.column_width(2, 150)

        update_table()

    def show_add_pledge_window(self):
        add_pledge_window = tk.Toplevel(self.window)
        add_pledge_window.title("Добавить залог")
        add_pledge_window.geometry("400x650")
        add_pledge_window.config(bg="#f5f5f5")
        add_pledge_window.resizable(False, False)

        tk.Label(add_pledge_window, text="Тип клиента:", font=("Arial", 14), bg="#f5f5f5").pack(pady=10)
        client_type_var = tk.StringVar(value="Обычный человек")

        def toggle_address_field():
            if client_type_var.get() == "Госслужащий":
                address_entry.config(state="disabled")
                address_entry.delete(0, tk.END)
            else:
                address_entry.config(state="normal")

        tk.Radiobutton(add_pledge_window, text="Обычный человек", variable=client_type_var, value="Обычный человек",
                       font=("Arial", 12), bg="#f5f5f5", command=toggle_address_field).pack(anchor="w", padx=20)
        tk.Radiobutton(add_pledge_window, text="Госслужащий", variable=client_type_var, value="Госслужащий",
                       font=("Arial", 12), bg="#f5f5f5", command=toggle_address_field).pack(anchor="w", padx=20)

        tk.Label(add_pledge_window, text="Имя:", font=("Arial", 14), bg="#f5f5f5").pack(pady=5)
        name_entry = tk.Entry(add_pledge_window, font=("Arial", 12), bg="#fff")
        name_entry.pack(pady=5)

        tk.Label(add_pledge_window, text="Номер паспорта (6 цифр):", font=("Arial", 14), bg="#f5f5f5").pack(pady=5)
        passport_entry = tk.Entry(add_pledge_window, font=("Arial", 12), bg="#fff")
        passport_entry.pack(pady=5)

        tk.Label(add_pledge_window, text="Адрес проживания:", font=("Arial", 14), bg="#f5f5f5").pack(pady=5)
        address_entry = tk.Entry(add_pledge_window, font=("Arial", 12), bg="#fff")
        address_entry.pack(pady=5)

        tk.Label(add_pledge_window, text="Вещи в залог:", font=("Arial", 14), bg="#f5f5f5").pack(pady=5)
        item_list = []

        item_count_label = tk.Label(add_pledge_window, text="Добавлено вещей: 0", font=("Arial", 12), bg="#f5f5f5")
        item_count_label.pack(pady=5)

        def update_item_count():
            item_count_label.config(text=f"Добавлено вещей: {len(item_list)}")

        def add_item():
            item_type_window = tk.Toplevel(add_pledge_window)
            item_type_window.title("Выберите тип вещи")
            item_type_window.geometry("300x200")
            item_type_window.config(bg="#f5f5f5")
            item_type_window.resizable(False, False)

            tk.Label(item_type_window, text="Выберите тип вещи:", font=("Arial", 14), bg="#4CAF50", fg="white").pack(fill='x', pady=10)

            def add_gold_item():
                item_window = tk.Toplevel(item_type_window)
                item_window.title("Добавить золотую вещь")
                item_window.geometry("400x300")
                item_window.config(bg="#f5f5f5")
                item_window.resizable(False, False)

                tk.Label(item_window, text="Название:", font=("Arial", 12), bg="#f5f5f5").pack(pady=5)
                name = tk.Entry(item_window, font=("Arial", 12), bg="#fff")
                name.pack(pady=5)

                tk.Label(item_window, text="Вес (г):", font=("Arial", 12), bg="#f5f5f5").pack(pady=5)
                weight = tk.Entry(item_window, font=("Arial", 12), bg="#fff")
                weight.pack(pady=5)

                tk.Label(item_window, text="Проба:", font=("Arial", 12), bg="#f5f5f5").pack(pady=5)
                proba = tk.Entry(item_window, font=("Arial", 12), bg="#fff")
                proba.pack(pady=5)

                def save_gold_item():
                    try:
                        item_name = name.get()
                        if not item_name.strip():
                            raise ValueError("Название не может быть пустым.")

                        if not weight.get().replace('.', '', 1).isdigit():
                            raise ValueError("Вес должен быть числовым значением.")
                        item_weight = float(weight.get())
                        if item_weight <= 0:
                            raise ValueError("Вес должен быть положительным числом.")

                        if not proba.get().isdigit():
                            raise ValueError("Проба должна быть целым числом.")
                        item_proba = int(proba.get())
                        if item_proba < 350:
                            raise ValueError("Проба должна быть целым числом в диапозоне [350, 1000].")

                        item_list.append(Gold(item_name, item_weight, item_proba))
                        item_window.destroy()
                        update_item_count()
                        print(f"Успешно добавлено: {item_name}, вес: {item_weight}, проба: {item_proba}")

                    except ValueError as e:
                        tk.messagebox.showerror("Ошибка ввода данных", f"Ошибка: {str(e)}")
                    except Exception as e:
                        tk.messagebox.showerror("Ошибка", f"Произошла неизвестная ошибка: {str(e)}")

                save_button = tk.Button(item_window, text="Сохранить", font=("Arial", 12), bg="#4CAF50", fg="white",
                                        command=save_gold_item)
                save_button.pack(pady=10)
                self.add_hover_effect(save_button)

            def add_fur_item():
                item_window = tk.Toplevel(item_type_window)
                item_window.title("Добавить мех")
                item_window.geometry("400x350")
                item_window.config(bg="#f5f5f5")
                item_window.resizable(False, False)

                tk.Label(item_window, text="Название:", font=("Arial", 12), bg="#f5f5f5").pack(pady=5)
                name = tk.Entry(item_window, font=("Arial", 12), bg="#fff")
                name.pack(pady=5)

                tk.Label(item_window, text="Вес (г):", font=("Arial", 12), bg="#f5f5f5").pack(pady=5)
                weight = tk.Entry(item_window, font=("Arial", 12), bg="#fff")
                weight.pack(pady=5)

                tk.Label(item_window, text="Стоимость меха за грамм:", font=("Arial", 12), bg="#f5f5f5").pack(pady=5)
                cost_fur = tk.Entry(item_window, font=("Arial", 12), bg="#fff")
                cost_fur.pack(pady=5)

                tk.Label(item_window, text="Степень износа (в процентах):", font=("Arial", 12), bg="#f5f5f5").pack(
                    pady=5)
                degree_wear = tk.Entry(item_window, font=("Arial", 12), bg="#fff")
                degree_wear.pack(pady=5)

                def save_fur_item():
                    try:
                        item_name = name.get()
                        if not item_name.strip():
                            raise ValueError("Название не может быть пустым.")

                        if not weight.get().replace('.', '', 1).isdigit():
                            raise ValueError("Вес должен быть числом")
                        item_weight = float(weight.get())
                        if item_weight <= 0:
                            raise ValueError("Вес должен быть положительным числом")

                        if not cost_fur.get().replace('.', '', 1).isdigit():
                            raise ValueError("Цена должна быть числом")
                        item_cost = float(cost_fur.get())
                        if item_cost <= 0:
                            raise ValueError("Цена должна быть положительным числом")

                        if not degree_wear.get().isdigit():
                            raise ValueError("Степень износа должна быть целым числом")

                        item_wear = int(degree_wear.get())
                        if item_wear < 0 or item_wear > 100:
                            raise ValueError("Степень износа в диапозоне [0, 100]")

                        item_list.append(Fur(item_name, item_weight, item_cost, item_wear))
                        item_window.destroy()
                        update_item_count()

                    except ValueError as e:
                        tk.messagebox.showerror("Ошибка ввода данных", f"Ошибка: {str(e)}")
                    except Exception as e:
                        tk.messagebox.showerror("Ошибка", f"Произошла неизвестная ошибка: {str(e)}")

                save_button = tk.Button(item_window, text="Сохранить", font=("Arial", 12), bg="#4CAF50", fg="white",
                                        command=save_fur_item)
                save_button.pack(pady=10)
                self.add_hover_effect(save_button)

            def add_appliance_item():
                item_window = tk.Toplevel(item_type_window)
                item_window.title("Добавить бытовую технику")
                item_window.geometry("400x300")
                item_window.config(bg="#f5f5f5")
                item_window.resizable(False, False)

                tk.Label(item_window, text="Название:", font=("Arial", 12), bg="#f5f5f5").pack(pady=5)
                name = tk.Entry(item_window, font=("Arial", 12), bg="#fff")
                name.pack(pady=5)

                tk.Label(item_window, text="Срок использования (лет):", font=("Arial", 12), bg="#f5f5f5").pack(pady=5)
                time_usage = tk.Entry(item_window, font=("Arial", 12), bg="#fff")
                time_usage.pack(pady=5)

                tk.Label(item_window, text="Стоимость нового аналога:", font=("Arial", 12), bg="#f5f5f5").pack(pady=5)
                cost_new = tk.Entry(item_window, font=("Arial", 12), bg="#fff")
                cost_new.pack(pady=5)

                def save_appliance_item():
                    try:
                        item_name = name.get()
                        if not item_name.strip():
                            raise ValueError("Название не может быть пустым.")

                        if not time_usage.get().replace('.', '', 1).isdigit():
                            raise ValueError("Срок использования должен быть числовым значением.")
                        item_usage = float(time_usage.get())
                        if item_usage < 0:
                            raise ValueError("Срок использования не может быть отрицательным.")

                        if not cost_new.get().replace('.', '', 1).isdigit():
                            raise ValueError("Стоимость должна быть числовым значением.")
                        item_cost = float(cost_new.get())
                        if item_cost <= 0:
                            raise ValueError("Стоимость должна быть положительным числом.")

                        item_list.append(Appliance(item_name, item_usage, item_cost))
                        item_window.destroy()
                        update_item_count()
                        print(
                            f"Успешно добавлено: {item_name}, срок использования: {item_usage} лет, стоимость нового аналога: {item_cost} руб.")

                    except ValueError as e:
                        tk.messagebox.showerror("Ошибка ввода данных", f"Ошибка: {str(e)}")
                    except Exception as e:
                        tk.messagebox.showerror("Ошибка", f"Произошла неизвестная ошибка: {str(e)}")

                save_button = tk.Button(item_window, text="Сохранить", font=("Arial", 12), bg="#4CAF50", fg="white",
                                        command=save_appliance_item)
                save_button.pack(pady=10)
                self.add_hover_effect(save_button)

            tk.Button(item_type_window, text="Золотая вещь", font=("Arial", 12), bg="#FFD700",
                      command=add_gold_item).pack(pady=5)
            tk.Button(item_type_window, text="Мех", font=("Arial", 12), bg="#A52A2A", command=add_fur_item).pack(pady=5)
            tk.Button(item_type_window, text="Бытовая техника", font=("Arial", 12), bg="#4682B4",
                      command=add_appliance_item).pack(pady=5)

        button1 = tk.Button(add_pledge_window, text="Добавить вещь", font=("Arial", 12), bg="#4CAF50", fg="white",
                            command=add_item)
        button1.pack(pady=10)
        self.add_hover_effect(button1)

        tk.Label(add_pledge_window, text="Выберите срок займа (дней):", font=("Arial", 14), bg="#f5f5f5").pack(pady=5)
        loan_term_var = tk.IntVar(value=15)
        for days in [15, 30, 45, 60]:
            tk.Radiobutton(add_pledge_window, text=f"{days} дней", variable=loan_term_var, value=days,
                           font=("Arial", 12), bg="#f5f5f5").pack(anchor="w", padx=20)

        def save_pledge():
            try:
                name = name_entry.get()
                passport = passport_entry.get()
                address = address_entry.get()

                if not name.strip():
                    raise ValueError("Имя не может быть пустым.")

                if not passport.isdigit() or len(passport) != 6:
                    raise ValueError("Номер паспорта должен содержать ровно 6 цифр.")

                if client_type_var.get() == "Обычный человек" and not address.strip():
                    raise ValueError("Адрес проживания обязателен для обычных людей.")

                if client_type_var.get() == "Обычный человек":
                    person = Person(name, int(passport), address)
                else:
                    person = GosPerson(name, int(passport))

                loan_term = loan_term_var.get()
                pledge = Pledge(person, item_list, loan_term, self.current_day)
                self.pledges.append(pledge)
                self.expenses_each_day[self.current_day] += pledge.loan
                self.update_pledges()
                add_pledge_window.destroy()

            except ValueError as e:
                tk.messagebox.showerror("Ошибка ввода данных", str(e))

            except Exception as e:
                tk.messagebox.showerror("Неизвестная ошибка", f"Произошла ошибка: {str(e)}")

        save_button = tk.Button(add_pledge_window, text="Добавить залог", command=save_pledge, font=("Arial", 12), bg="#4CAF50", fg="white")
        save_button.pack()
        self.add_hover_effect(save_button)

    def show_income_expense_chart(self):
        dates = [self.start_date + timedelta(days=day - 1) for day in self.income_each_day.keys()]
        incomes = list(self.income_each_day.values())
        expenses = list(self.expenses_each_day.values())

        plt.figure(figsize=(12, 6))
        plt.plot(dates, incomes, label="Доходы", color="green", marker='.')
        plt.plot(dates, expenses, label="Расходы", color="red", marker='.')

        plt.title("Доходы и расходы по дням", fontsize=16)
        plt.xlabel("Дата", fontsize=14)
        plt.ylabel("Суммы (руб.)", fontsize=14)
        plt.legend(fontsize=12)
        plt.grid(True)

        def format_yaxis(value, _):
            if value >= 1_000_000:
                return f"{value / 1_000_000:.1f}M"
            elif value >= 1_000:
                return f"{value / 1_000:.1f}K"
            else:
                return str(int(value))

        plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(format_yaxis))

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))
        plt.gcf().autofmt_xdate(rotation=45, ha='right')

        plt.tight_layout()
        plt.show()

    @staticmethod
    def read_pledges_from_csv(file_path):
        pledges = []
        with open(file_path, encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Class'] == 'GosPerson':
                    person = GosPerson(name=row['PersonName'], number=row['PersonNumber'])
                elif row['Class'] == 'Person':
                    person = Person(
                        name=row['PersonName'],
                        number=row['PersonNumber'],
                        home_address=row['Address']
                    )

                item_types = row['ItemTypes'].split(';')
                item_params_list = row['ItemParams'].split(';')

                items = []
                for item_type, item_params in zip(item_types, item_params_list):
                    params = item_params.split(',')

                    if item_type == 'Gold':
                        item = Gold(name=params[0], weight=float(params[1]), proba=int(params[2]))
                    elif item_type == 'Fur':
                        item = Fur(name=params[0], weight=float(params[1]),
                                   cost_fur=float(params[2]), degree_wear=float(params[3]))
                    elif item_type == 'Appliance':
                        item = Appliance(name=params[0], time_usage=int(params[1]),
                                         cost_new_analog=float(params[2]))
                    items.append(item)
                loan_term = int(row['LoanTerm'])
                pledge = Pledge(person=person, items=items, loan_term=loan_term)
                pledges.append(pledge)

        return pledges

    def start(self):
        self.create_widgets()
        self.window.mainloop()

p = Pawnshop()
p.start()
