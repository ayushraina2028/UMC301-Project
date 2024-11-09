import pandas as pd
import streamlit as st
from streamlit_pills import pills

# Read the CSV file
csv_file = '../ExtractedEmails/emails_metadata.csv'  # Update with the correct path to your CSV file
df = pd.read_csv(csv_file)

# Use Streamlit Pills to select the category
selected = pills("Select Category", ["Offers", "Reminder/Alerts", "Events"], ["🍀", "🎈", "🌈"])

# Filter the data based on the selected category
if selected:
    filtered_df = df[df['category'] == selected]
    
    # Display the filtered data
    if not filtered_df.empty:
        st.write(f"Showing emails for category: {selected}")
        for index, row in filtered_df.iterrows():
            st.subheader(row['email_title'])
            st.write(f"**Summary**: {row['summary_text']}")
            st.write(f"**Promo Code**: {row['promo_code']}")
            st.write(f"**Expiry Date**: {row['expiry_date']}")
            st.write("---")
    else:
        st.write(f"No emails found for category: {selected}")
