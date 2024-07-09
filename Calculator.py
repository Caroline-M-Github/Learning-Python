import tkinter as tk
import math

class Calculator:
    def __init__(self, master):
        self.master = master
        master.title("Calculator")
        master.configure(bg='#f0f0f0')

        self.entry = tk.Entry(master, width=18, font=('Arial', 24), borderwidth=2, relief='solid', justify='right')
        self.entry.grid(row=0, column=0, columnspan=5, padx=10, pady=10, sticky='nsew')

        self.create_buttons()
        self.bind_keys()

    def create_buttons(self):
        buttons = [
            ('(', 1, 0), (')', 1, 1), ('C', 1, 2), ('⌫', 1, 3), ('sqrt', 1, 4),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2), ('+', 2, 3), ('sin', 2, 4),
            ('4', 3, 0), ('5', 3, 1), ('6', 3, 2), ('-', 3, 3), ('cos', 3, 4),
            ('1', 4, 0), ('2', 4, 1), ('3', 4, 2), ('*', 4, 3), ('tan', 4, 4),
            ('0', 5, 0), ('.', 5, 1), ('+/-', 5, 2), ('/', 5, 3), ('=', 5, 4)
        ]

        for button_info in buttons:
            text, row, column = button_info
            color = self.get_button_color(text)
            self.create_button(text, row, column, lambda x=text: self.button_click(x), color)

    def create_button(self, text, row, column, command, color='#e0e0e0'):
        button = tk.Button(self.master, text=text, padx=20, pady=20, font=('Arial', 14),
                           command=command, bg=color, fg='black', activebackground='#c0c0c0')
        button.grid(row=row, column=column, sticky='nsew', padx=2, pady=2)

    def get_button_color(self, text):
        if text in ('C','(', ')', '⌫'):
            return '#ff6347'
        elif text in ('+', '-', '*', '/'):
            return '#ffa500'
        elif text in ('='):
            return '#cc00ff'
        elif text in ('sqrt', 'sin', 'cos', 'tan'):
            return '#4169e1'
        else:
            return '#e0e0e0'

    def button_click(self, value):
        if value == '=':
            self.calculate()
        elif value == 'C':
            self.clear()
        elif value == '⌫':
            self.backspace()
        elif value == '+/-':
            self.negate()
        elif value in ('sqrt', 'sin', 'cos', 'tan'):
            self.apply_function(value)
        else:
            self.entry.insert(tk.END, value)

    def clear(self):
        self.entry.delete(0, tk.END)

    def backspace(self):
        current = self.entry.get()
        self.entry.delete(0, tk.END)
        self.entry.insert(0, current[:-1])

    def negate(self):
        try:
            value = float(self.entry.get())
            self.entry.delete(0, tk.END)
            self.entry.insert(0, str(-value))
        except ValueError:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, "Error")

    def apply_function(self, func):
        try:
            value = float(self.entry.get())
            if func == 'sqrt':
                result = math.sqrt(value)
            elif func == 'sin':
                result = math.sin(math.radians(value))
            elif func == 'cos':
                result = math.cos(math.radians(value))
            elif func == 'tan':
                result = math.tan(math.radians(value))
            self.entry.delete(0, tk.END)
            self.entry.insert(0, str(result))
        except ValueError:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, "Error")

    def calculate(self):
        try:
            result = eval(self.entry.get())
            self.entry.delete(0, tk.END)
            self.entry.insert(0, str(result))
        except Exception as e:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, "Error")

    def bind_keys(self):
        self.master.bind('<Return>', lambda event: self.calculate())
        self.master.bind('<BackSpace>', lambda event: self.backspace())
        for key in '0123456789+-*/().':
            self.master.bind(key, lambda event, digit=key: self.entry.insert(tk.END, digit))

if __name__ == "__main__":
    root = tk.Tk()
    calculator = Calculator(root)
    for i in range(6):  # 6 rows including the entry field
        root.grid_rowconfigure(i, weight=1)
    for i in range(5):  # 5 columns
        root.grid_columnconfigure(i, weight=1)
    root.mainloop()
