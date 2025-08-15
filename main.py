import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


# Ensure files exist
if not os.path.exists('activities.csv'):
    pd.DataFrame(columns=['Activity', 'Start Time', 'End Time', 'Duration', 'Notes']).to_csv('activities.csv', index=False)

if not os.path.exists('activity_list.txt'):
    with open('activity_list.txt', 'w') as f:
        f.write("Study\nGame\nWatch YouTube\nDo Anything Unuseful")

# Load activities
with open('activity_list.txt', 'r') as f:
    activities = f.read().splitlines()

# Load data
df = pd.read_csv('activities.csv')

# Variables
current_activity = None
start_timestamp = None
current_notes = None

# Initialize UI
root = tk.Tk()
root.title("Activity Tracker")
root.geometry("600x400")

# Center window
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (600 // 2)
y = (screen_height // 2) - (400 // 2)
root.geometry(f"600x400+{x}+{y}")

# Main Frame
main_frame = tk.Frame(root, padx=10, pady=10)
main_frame.pack(expand=True, fill="both")

# Activity Dropdown
activity_var = tk.StringVar()
activity_label = tk.Label(main_frame, text="Select Activity:")
activity_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

activity_menu = ttk.Combobox(main_frame, textvariable=activity_var, values=activities)
activity_menu.grid(row=0, column=1, padx=5, pady=5)

# Notes Entry
notes_label = tk.Label(main_frame, text="Notes:")
notes_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

notes_entry = tk.Entry(main_frame, width=40)
notes_entry.grid(row=1, column=1, padx=5, pady=5)

# Activity Status
activity_status = tk.Label(main_frame, text="No activity running.", fg="red")
activity_status.grid(row=2, column=0, columnspan=2, pady=10)

# Timer
timer_label = tk.Label(main_frame, text="")
timer_label.grid(row=3, column=0, columnspan=2, pady=5)

# Status Label
status_label = tk.Label(main_frame, text="", fg="black")
status_label.grid(row=10, column=0, columnspan=2, pady=5)

# Start Activity
def start_activity():
    global current_activity, start_timestamp, current_notes
    activity = activity_var.get()
    notes = notes_entry.get()

    if not activity:
        status_label.config(text="Please select an activity!", fg="red")
        return

    current_activity = activity
    if notes:
        current_notes = notes
    else:
        current_notes = "No notes"
    start_timestamp = datetime.now()

    activity_status.config(text=f"Running: {activity}", fg="green")
    status_label.config(text=f"Started at {start_timestamp.strftime('%H:%M:%S')}", fg="green")
    update_timer()

# Update Timer
def update_timer():
    if current_activity:
        elapsed_time = datetime.now() - start_timestamp
        timer_label.config(text=f"Elapsed time: {elapsed_time}")
        root.after(1000, update_timer)

# Stop Activity
def stop_activity():
    global current_activity, start_timestamp, current_notes, df
    if not current_activity:
        status_label.config(text="No activity is running!", fg="red")
        return

    end_time = datetime.now()
    duration = end_time - start_timestamp

    # Create a new DataFrame for the new activity
    new_entry = pd.DataFrame([{
        'Activity': current_activity,
        'Start Time': start_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'End Time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
        'Duration': duration.total_seconds() / 3600,
        'Notes': current_notes
    }])

    # If the CSV is empty, replace df instead of concatenating
    if df.empty:
        df = new_entry
    else:
        df = pd.concat([df, new_entry], ignore_index=True)

    df.to_csv('activities.csv', index=False)

    activity_status.config(text="No activity running.", fg="red")
    timer_label.config(text="")
    status_label.config(text=f"Stopped after {duration}", fg="blue")

    current_activity = None
    start_timestamp = None
    current_notes = None

# Add New Activity
def add_activity():
    new_activity = new_activity_entry.get()
    if new_activity:
        activities.append(new_activity)
        activity_menu['values'] = activities
        delete_activity_menu['values'] = activities
        with open('activity_list.txt', 'a') as f:
            f.write(f"\n{new_activity}")
        status_label.config(text=f"Added: {new_activity}", fg="green")

# Delete Activity
def delete_activity():
    activity_to_delete = delete_activity_var.get()
    if not activity_to_delete:
        status_label.config(text="Please select an activity to delete!", fg="red")
        return

    if activity_to_delete in activities:
        activities.remove(activity_to_delete)
        activity_menu['values'] = activities
        delete_activity_menu['values'] = activities
        with open('activity_list.txt', 'w') as f:
            f.write("\n".join(activities))
        status_label.config(text=f"Deleted: {activity_to_delete}", fg="blue")

# Show Analysis
def show_analysis():
    if df.empty:
        messagebox.showinfo("Analysis", "No activity data available!")
        return

    df['Start Time'] = pd.to_datetime(df['Start Time'])
    df['Date'] = df['Start Time'].dt.date

    # Group and plot the data
    daily_summary = df.groupby(['Date', 'Activity'])['Duration'].sum().unstack(fill_value=0)
    ax = daily_summary.plot(kind='bar', stacked=True, figsize=(10, 6))

    plt.title('Time Analysis')
    plt.xlabel('Date')
    plt.ylabel('Hours Spent')
    plt.legend(title="Activity", bbox_to_anchor=(1.05, 1), loc='upper left')

    # Save the graph as an image
    plt.tight_layout()
    plt.savefig("activity_analysis.png")
    plt.close()

    messagebox.showinfo("Analysis Saved", "Activity analysis saved as 'activity_analysis.png'")
# Generate Report
def generate_report():
    start_date = start_date_entry.get()
    end_date = end_date_entry.get()

    if not start_date or not end_date:
        messagebox.showwarning("Input Error", "Please enter both start and end dates!")
        return

    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        messagebox.showwarning("Input Error", "Invalid date format! Use YYYY-MM-DD.")
        return

    # Ensure 'Start Time' is treated as datetime
    df['Start Time'] = pd.to_datetime(df['Start Time'])

    # Filter activities within the date range
    report_df = df[(df['Start Time'].dt.date >= start_dt.date()) & (df['Start Time'].dt.date <= end_dt.date())]

    if report_df.empty:
        messagebox.showinfo("Report", "No activity found in this date range.")
        return

    # Generate a PDF report
    filename = f"Activity_Report_{start_date}_to_{end_date}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    c.setFont("Helvetica", 12)

    y_position = 800  # Start position for writing text
    c.drawString(200, y_position, f"Activity Report ({start_date} to {end_date})")
    y_position -= 30

    for date, group in report_df.groupby(report_df['Start Time'].dt.date):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, str(date))
        y_position -= 20
        c.setFont("Helvetica", 10)

        for _, row in group.iterrows():
            start_time = row['Start Time'].strftime("%H:%M:%S")
            end_time = datetime.strptime(row['End Time'], "%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S")

            # Convert duration to hours, minutes, seconds
            total_seconds = int(float(row["Duration"]) * 3600)
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            activity_text = f"From {start_time} to {end_time}"
            c.drawString(70, y_position, activity_text)
            y_position -= 15

            c.drawString(90, y_position, f"There was activity: {row['Activity']}")
            y_position -= 15

            c.drawString(90, y_position, f"Notes: {row['Notes']}")
            y_position -= 15

            c.drawString(90, y_position, f"Duration: {hours} hours, {minutes} minutes, {seconds} seconds")
            y_position -= 25  # Space between activities

            if y_position < 50:  # Start a new page if space is low
                c.showPage()
                y_position = 800
                c.setFont("Helvetica", 10)

    c.save()
    messagebox.showinfo("Report Generated", f"Report saved as {filename}")
# Buttons
button_frame = tk.Frame(main_frame)
button_frame.grid(row=4, column=0, columnspan=2, pady=10)

tk.Button(button_frame, text="Start Activity", command=start_activity).grid(row=0, column=0, padx=5)
tk.Button(button_frame, text="Stop Activity", command=stop_activity).grid(row=0, column=1, padx=5)
tk.Button(button_frame, text="Show Analysis", command=show_analysis).grid(row=0, column=2, padx=5)

# Add & Delete Activities
new_activity_entry = tk.Entry(main_frame, width=20)
new_activity_entry.grid(row=5, column=0, padx=5, pady=5)
tk.Button(main_frame, text="Add Activity", command=add_activity).grid(row=5, column=1, padx=5, pady=5)

delete_activity_var = tk.StringVar()
delete_activity_menu = ttk.Combobox(main_frame, textvariable=delete_activity_var, values=activities)
delete_activity_menu.grid(row=6, column=0, padx=5, pady=5)
tk.Button(main_frame, text="Delete Activity", command=delete_activity).grid(row=6, column=1, padx=5, pady=5)

# Report
tk.Label(main_frame, text="Start Date (YYYY-MM-DD):").grid(row=7, column=0)
start_date_entry = tk.Entry(main_frame)
start_date_entry.grid(row=7, column=1)

tk.Label(main_frame, text="End Date (YYYY-MM-DD):").grid(row=8, column=0)
end_date_entry = tk.Entry(main_frame)
end_date_entry.grid(row=8, column=1)

tk.Button(main_frame, text="Generate Report", command=generate_report).grid(row=9, column=0, columnspan=2, pady=5)

root.mainloop()