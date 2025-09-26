import tkinter as tk
import requests
import dotenv
import os
import sheets
from tkinter import ttk, messagebox
from dotenv import load_dotenv
from requests import ConnectTimeout

load_dotenv()

SERVER_URL = os.getenv("SERVER_URL")

round_and_adds = {}

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
    class_parent = None

    def __init__(self, parent):
        super().__init__(parent)
        self.class_parent = parent

        self.btn_new_table = ttk.Button(self, text="Add Round", command=self.getWindowNewTable)
        self.btn_new_table.grid(row=0, column=0)

        self.btn_insert = ttk.Button(self, text="Add Address", command=self.getWindowInsertAddress)
        self.btn_insert.grid(row=0, column=1)

        self.btn_delete = ttk.Button(self, text="Remove Address", command=self.getWindowDeleteAddress)
        self.btn_delete.grid(row=0, column=2)

        self.btn_drop_table = ttk.Button(self, text="Remove Round")
        self.btn_drop_table.grid(row=0, column=3)

        self.btn_rollback = ttk.Button(self, text="Rollback Round")
        self.btn_rollback.grid(row=0, column=4)

        self.btn_job_sheet = ttk.Button(self, text="Optimise Job Sheet", command=self.optimiseJobSheetButton)
        self.btn_job_sheet.grid(row=0, column=6)

        self.label_load = ttk.Label(self, text="Test")
        self.label_load.grid(row=1, column=3)
    
    def getWindowNewTable(self):
        nt_win = WindowNewTable(self.class_parent)
    
    def getWindowInsertAddress(self):
        inad_win = WindowInsertAddress(self.class_parent)
    
    def getWindowDeleteAddress(self):
        delad_win = WindowDeleteAddress(self.class_parent)
    
    def optimiseJobSheetButton(self):
        self.label_load.config(text="Optimising Job Sheet...")
        outcome = sheets.optimiseJobSheet()
        if outcome:
           self.message = messagebox.showerror(message=f"""Error code {outcome.status_code}, 
                                                sheet not optimised\n {outcome.reason}""")
           self.label_load.config(text=f"Error while optimising jobsheet, {outcome.status_code}")
        else:
           self.label_load.config(text="Job Sheet Optimised")
           print(round_and_adds)

class RoundDisplay(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        key_list = []
        for key in round_and_adds.keys():
            key_list.append(key)

        self.n = tk.StringVar()
        self.roundchosen = ttk.Combobox(self, width = 27, textvariable = self.n)
        self.roundchosen['values'] = key_list
        self.roundchosen['state'] = 'readonly'
        self.roundchosen.grid(row=0, column=0, sticky="n")
        self.roundchosen.current()
        self.roundchosen.bind('<<ComboboxSelected>>', self.load_addresses)

        self.list_addresses = tk.Listbox(self)
        self.list_addresses.grid(row=0, column=1)

        self.btn_fetch = ttk.Button(self, text="Fetch Rounds", command=self.fetch_rounds)
        self.btn_fetch.grid(row=1, column=0, sticky="n")
    
    def fetch_rounds(self):
        try:
            response = requests.post(f"{SERVER_URL}/refresh").json()
            global round_and_adds
            round_and_adds = response["all_data"]
            key_list = []
            for key in round_and_adds.keys():
                key_list.append(key)
        except Exception as e:
            print(e)
        
        self.roundchosen.config(values=key_list, textvariable="")
        self.roundchosen.set("")
        self.list_addresses.delete(0, tk.END)
    
    def load_addresses(self, event=None):
        rd = self.roundchosen.get()
        if rd:
            self.list_addresses.delete(0, tk.END)
            for add in round_and_adds[rd]:
                self.list_addresses.insert(tk.END, f"{add[0]} {add[1]}")

class WindowNewTable(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("New Round")

        self.label = ttk.Label(self, text="Please enter a name for the round")
        self.label.grid(row=0, column=0)

        self.entry = ttk.Entry(self)
        self.entry.grid(row=1, column=0)

        self.entry_btn = ttk.Button(self, text="Enter", command=self.create_table)
        self.entry_btn.grid(row=1, column=1)
    
    def create_table(self):
        table_name = self.entry.get()

        try:
            response = requests.post(f"{SERVER_URL}/create_table", json={"table": table_name})

            if response.status_code != 200:
                self.message = messagebox.showerror(message=f"Error code {response.status_code}, round not created")
            else:
                self.message = messagebox.showinfo(message=response.text)
        except (TimeoutError, ConnectTimeout):
            self.message = messagebox.showerror(message=f"Request timeout, ensure server is on & running")
        finally:
            self.destroy()

class WindowInsertAddress(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        key_list = []
        for key in round_and_adds.keys():
            key_list.append(key)

        self.title = "Insert Address"
        self.label_info = ttk.Label(self, text="""Please select a round and enter the address.
        Example Address: 0/1 1 House St G11 3LA""")
        self.label_info.grid(row=0, column=0)

        self.label_street = ttk.Label(self, text="Street")
        self.label_street.grid(row=1, column=1)

        self.label_postcode = ttk.Label(self, text="Postcode")
        self.label_postcode.grid(row=1, column=2)

        self.n = tk.StringVar()
        self.roundchosen = ttk.Combobox(self, width = 27, textvariable = self.n)
        self.roundchosen['values'] = key_list
        self.roundchosen['state'] = 'readonly'
        self.roundchosen.grid(row=2, column=0)
        self.roundchosen.current()
        self.roundchosen.bind('<<ComboboxSelected>>', self.buttonEnable)

        self.entry_street = ttk.Entry(self)
        self.entry_street.grid(row=2, column=1)

        self.entry_postcode = ttk.Entry(self)
        self.entry_postcode.grid(row=2, column=2)

        self.btn_entry = ttk.Button(self, text="Please select a round")
        self.btn_entry.grid(row=3, column=0)
    
    def buttonEnable(self, event=None):
        self.btn_entry.config(text="Insert Address", command=self.insert_address)
    
    def insert_address(self):
        table = self.roundchosen.get()
        street = self.entry_street.get()
        postcode = self.entry_postcode.get()
        if table and street and postcode:
            try:
                response = requests.post(f"{SERVER_URL}/insert_value", json={"table": table, 
                                        "address": (street, postcode)})
                
                if response.status_code != 200:
                    self.message = messagebox.showerror(message=f"Error code {response.status_code}, address not inserted")
                else:
                    self.message = messagebox.showinfo(message=response.text)
            except (TimeoutError, ConnectTimeout):
                self.message = messagebox.showerror(message=f"Request timeout, ensure server is on & running")
            finally:
                self.destroy()

class WindowDeleteAddress(tk.Toplevel):

    def __init__(self, parent):
        super().__init__(parent)

        self.ix_tracker = -1

        key_list = []
        for key in round_and_adds.keys():
            key_list.append(key)
        
        self.title = "Delete Address"
        self.label_info = ttk.Label(self, text="""Please select a round and address to delete.""")
        self.label_info.grid(row=0, column=0)

        self.label_round = ttk.Label(self, text="Round")
        self.label_round.grid(row=1, column=0)

        self.label_address = ttk.Label(self, text="Street")
        self.label_address.grid(row=1, column=1)

        self.round = tk.StringVar()
        self.roundchosen = ttk.Combobox(self, width = 27, textvariable = self.round)
        self.roundchosen['values'] = key_list
        self.roundchosen['state'] = 'readonly'
        self.roundchosen.bind('<<ComboboxSelected>>', self.load_addresses)
        self.roundchosen.grid(row=2, column=0)
        self.roundchosen.current()

        self.add = tk.StringVar()
        self.addchosen = ttk.Combobox(self, width = 27, textvariable = self.add)
        self.addchosen.bind("<<ComboboxSelected>>", self.track_index)
        self.addchosen['state'] = 'readonly'
        self.addchosen.grid(row=2, column=1)
        self.addchosen.current()

        self.button_del = ttk.Button(self, text="Delete Address", command=self.delete_address)
        self.button_del.grid(row=3, column=0)
    
    def track_index(self, event=None):
        self.ix_tracker = self.addchosen.current()
    
    def load_addresses(self, event=None):
        rd = self.roundchosen.get()
        if rd:
            self.addchosen.set("")
            self.addchosen.config(values=round_and_adds[rd])

    def delete_address(self):
        rd = self.roundchosen.get()
        add_check = self.addchosen.get() # solely just to check an address has been selected will use index later
        if rd and add_check:
            outcome = messagebox.askyesno(title="Confirm Deletion",
            message=f"Delete {round_and_adds[rd][self.ix_tracker]} from {rd}?")

            if outcome:
                try:
                    response = requests.post(f"{SERVER_URL}/delete_value", json={"table": rd,
                                                "address": round_and_adds[rd][self.ix_tracker]})
                    if response.status_code != 200:
                        self.message = messagebox.showerror(message=f"Error code {response.status_code}, address not deleted")
                    else:
                        self.message = messagebox.showinfo(message=response.text)
                except (TimeoutError, ConnectTimeout):
                    self.message = messagebox.showerror(message=f"Request timeout, ensure server is on & running")
                finally:
                    self.destroy()

            self.destroy()

def main():
    app = Application()
    app.mainloop()

if __name__ == "__main__":
    main()
