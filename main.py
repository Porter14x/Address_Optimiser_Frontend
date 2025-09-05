import tkinter as tk

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Address Optimiser")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

def main():
    app = Application()
    app.mainloop()

if __name__ == "__main__":
    main()
