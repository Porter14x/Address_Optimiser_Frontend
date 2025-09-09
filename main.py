import tkinter as tk
from tkinter import ttk

round_and_adds = {
    "G81": [("1 House St", "G81"), ("2 House St", "G81"), ("3 House St", "G81")],
    "G82": [("1 House Dr", "G82"), ("2 House Dr", "G82"), ("3 House Dr", "G82")],
    "G83": [("1 House Av", "G83"), ("2 House Av", "G83"), ("3 House Av", "G83")],
}

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Address Optimiser")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        frame_btn = ButtonRow(self)
        frame_btn.grid(row=0, column=0)

        frame_display = RoundDisplay(self)
        frame_display.grid(row=1, column=0)

class ButtonRow(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.btn_new_table = ttk.Button(self, text="Add Round")
        self.btn_new_table.grid(row=0, column=0)

        self.btn_insert = ttk.Button(self, text="Add Address")
        self.btn_insert.grid(row=0, column=1)

        self.btn_delete = ttk.Button(self, text="Remove Address")
        self.btn_delete.grid(row=0, column=2)

        self.btn_drop_table = ttk.Button(self, text="Remove Round")
        self.btn_drop_table.grid(row=0, column=3)

        self.btn_rollback = ttk.Button(self, text="Rollback Round")
        self.btn_rollback.grid(row=0, column=4)

        self.btn_batch_insert = ttk.Button(self, text="Insert From Sheet")
        self.btn_batch_insert.grid(row=0, column=5)

        self.btn_job_sheet = ttk.Button(self, text="Optimise Job Sheet")
        self.btn_job_sheet.grid(row=0, column=6)

class RoundDisplay(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.n = tk.StringVar()
        self.roundchosen = ttk.Combobox(self, width = 27, textvariable = self.n)
        self.roundchosen['values'] = [
            "G81",
            "G82",
            "G83",
        ]
        self.roundchosen['state'] = 'readonly'
        self.roundchosen.grid(row=0, column=0, sticky="n")
        self.roundchosen.current()
        self.roundchosen.bind('<<ComboboxSelected>>', self.load_addresses)

        self.list_addresses = tk.Listbox(self)
        self.list_addresses.grid(row=0, column=1)
    
    def load_addresses(self, event=None):
        rd = self.roundchosen.get()
        if rd:
            self.list_addresses.delete(0, tk.END)
            for add in round_and_adds[rd]:
                self.list_addresses.insert(tk.END, f"{add[0]} {add[1]}")

def main():
    app = Application()
    app.mainloop()

if __name__ == "__main__":
    main()
