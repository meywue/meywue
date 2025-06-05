import tkinter as tk
from tkinter import messagebox

def on_select(event):
  selected = listbox.get(listbox.curselection())
  messagebox.showinfo("You selected", selected)

def main():
  # Create the main window
  root = tk.Tk()
  root.title("Simple List")
  root.geometry("300x200")

  # Create a listbox widget
  listbox = tk.Listbox(root)
  items = ["Apples", "Bananas", "Cherries", "Dates", "Elderberries"]
  for item in items:
    listbox.insert(tk.END, item)

  listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
  listbox.bind("<<ListboxSelect>>", on_select)

  # Start the GUI event loop
  root.mainloop()

if __name__ == "__main__":
  main()