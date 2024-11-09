import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# Assuming you have already defined the email processing and API fetching functions

# Global set to track the subjects of the displayed emails
displayed_emails = set()

def refresh_emails(tab, category):
    """Refresh emails for a specific category and update the displayed emails."""
    
    # Get the new emails for the category from your email API or file
    new_emails = fetch_new_emails(category)  # Replace this with the actual email fetching function

    # Loop through the new emails
    for email in new_emails:
        email_subject = email.get('subject')  # Assuming 'subject' key exists
        
        # If the subject hasn't been displayed yet, append it
        if email_subject not in displayed_emails:
            displayed_emails.add(email_subject)

            # Append email to the Treeview widget
            treeview_item = (email.get('pdf_filename'), email.get('title'), email.get('category'), email.get('summary'), email.get('promo_code'), email.get('expiry_date'))
            tab.insert('', 'end', values=treeview_item)

def fetch_new_emails(category):
    """Dummy function to simulate fetching emails for a category."""
    # This should be replaced with the actual logic to fetch emails from the Gmail API
    # For now, it returns some dummy emails for demonstration purposes.
    return [
        {"subject": f"New email for {category}", "pdf_filename": f"email_{category}.pdf", "title": f"Email {category} Title", "category": category, "summary": f"Summary of {category} email", "promo_code": "ABC123", "expiry_date": "2024-12-31"},
        # Add more dummy emails here
    ]

# Create the main window
root = tk.Tk()
root.title("Email App")

# Set the background color and size for the window
root.geometry("800x600")
root.config(bg="#f0f0f0")

# Create a Notebook widget for tabs
notebook = ttk.Notebook(root)
notebook.pack(pady=10, expand=True)

# Categories
categories = ['Offers', 'Events', 'Alerts/Reminders']

# Create a Treeview widget for each category
tabs = {}
for category in categories:
    tab = ttk.Treeview(notebook, columns=('PDF Filename', 'Title', 'Category', 'Summary', 'Promo Code', 'Expiry Date'), show='headings', height=10)
    
    # Define columns
    tab.heading('PDF Filename', text='PDF Filename')
    tab.heading('Title', text='Title')
    tab.heading('Category', text='Category')
    tab.heading('Summary', text='Summary')
    tab.heading('Promo Code', text='Promo Code')
    tab.heading('Expiry Date', text='Expiry Date')

    # Customize column widths
    tab.column('PDF Filename', width=150, anchor='w')
    tab.column('Title', width=250, anchor='w')
    tab.column('Category', width=100, anchor='center')
    tab.column('Summary', width=300, anchor='w')
    tab.column('Promo Code', width=100, anchor='center')
    tab.column('Expiry Date', width=100, anchor='center')

    # Style for rows and header
    tab.tag_configure('odd', background="#f9f9f9")
    tab.tag_configure('even', background="#ffffff")
    
    # Add the Treeview to the notebook
    notebook.add(tab, text=category)
    
    # Store the tab for later use
    tabs[category] = tab

# Style for the refresh button
button_style = {
    'bg': '#4CAF50',
    'fg': '#ffffff',
    'font': ('Arial', 12, 'bold'),
    'relief': 'flat',
    'padx': 20,
    'pady': 10
}

# Add a refresh button
def refresh_button_click():
    """Refresh emails when the refresh button is clicked."""
    try:
        for category in categories:
            refresh_emails(tabs[category], category)
        messagebox.showinfo("Success", "Emails refreshed successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

refresh_button = tk.Button(root, text="Refresh", command=refresh_button_click, **button_style)
refresh_button.pack(pady=20)

# Add an exit button
exit_button_style = {
    'bg': '#f44336',
    'fg': '#ffffff',
    'font': ('Arial', 12, 'bold'),
    'relief': 'flat',
    'padx': 20,
    'pady': 10
}

def exit_app():
    """Exit the application."""
    root.quit()

exit_button = tk.Button(root, text="Exit", command=exit_app, **exit_button_style)
exit_button.pack(pady=10)

# Run the Tkinter event loop
root.mainloop()
