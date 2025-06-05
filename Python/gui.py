import tkinter as tk
from tkinter import messagebox
from pathlib import Path

def on_select(event):
    widget = event.widget
    try:
        selected = widget.get(widget.curselection())
        messagebox.showinfo("You selected", selected)
    except tk.TclError:
        pass

def main():
    directory = Path(r"Z:\digital")

    root = tk.Tk()
    root.title("Listbox with Scrollbar")
    root.geometry("300x200")

    # Frame to contain both listbox and scrollbar
    frame = tk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Scrollbar FIRST
    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Then the listbox
    listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set)
    items = [str(d) for d in directory.iterdir() if d.is_dir()]
    for item in items:
        listbox.insert(tk.END, item)

    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Link scrollbar to listbox
    scrollbar.config(command=listbox.yview)

    # Bind selection
    listbox.bind("<<ListboxSelect>>", on_select)

    root.mainloop()

if __name__ == "__main__":
    main()
