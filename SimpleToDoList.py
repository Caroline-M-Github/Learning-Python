import tkinter as tk
from tkinter import messagebox

# Create the main window
root = tk.Tk()
root.title("To-Do List")

# Create a frame for the listbox and scrollbar
frame = tk.Frame(root)
frame.pack(pady=10)

# Create a listbox
listbox = tk.Listbox(
    frame,
    width=50,
    height=10,
    selectmode=tk.SINGLE,
    font=("Arial", 14)
)
listbox.pack(side=tk.LEFT, fill=tk.BOTH)

# Create a scrollbar
scrollbar = tk.Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)

listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=listbox.yview)

# Function to add a task
def add_task():
    task = task_entry.get()
    if task != "":
        listbox.insert(tk.END, task)
        task_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Warning", "You must enter a task.")

# Function to delete a task
def delete_task():
    try:
        selected_task_index = listbox.curselection()[0]
        listbox.delete(selected_task_index)
    except IndexError:
        messagebox.showwarning("Warning", "You must select a task.")

# Function to mark a task as completed
def complete_task():
    try:
        selected_task_index = listbox.curselection()[0]
        task = listbox.get(selected_task_index)
        listbox.delete(selected_task_index)
        listbox.insert(tk.END, f"{task} ✔️")
    except IndexError:
        messagebox.showwarning("Warning", "You must select a task.")

# Create an entry widget to add tasks
task_entry = tk.Entry(root, width=50)
task_entry.pack(pady=10)

# Create buttons to add, delete, and mark tasks as completed
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

add_button = tk.Button(button_frame, text="Add Task", command=add_task)
add_button.pack(side=tk.LEFT)

delete_button = tk.Button(button_frame, text="Delete Task", command=delete_task)
delete_button.pack(side=tk.LEFT)

complete_button = tk.Button(button_frame, text="Complete Task", command=complete_task)
complete_button.pack(side=tk.LEFT)

# Run the main event loop
root.mainloop()
