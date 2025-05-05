import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import json

# Initialize Firebase (only once)
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-admin-sdk.json")  # Download from Firebase console
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://voter-card-scanner-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })

# Firebase Realtime Database Reference
COMPLAINTS_REF = db.reference('/complaints')

# Firebase Operations
def save_complaint_to_firebase(complaint_data):
    try:
        new_ref = COMPLAINTS_REF.push()
        new_ref.set(complaint_data)
        return new_ref.key
    except Exception as e:
        st.error(f"Firebase save failed: {str(e)}")
        return None

def get_complaints_from_firebase():
    try:
        complaints = COMPLAINTS_REF.get()
        if complaints:
            return pd.DataFrame.from_dict(complaints, orient='index')
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Firebase read failed: {str(e)}")
        return pd.DataFrame()

def update_complaint_in_firebase(complaint_id, updates):
    try:
        COMPLAINTS_REF.child(complaint_id).update(updates)
        return True
    except Exception as e:
        st.error(f"Firebase update failed: {str(e)}")
        return False
def main():
    st.set_page_config(page_title="Election Complaint System", layout="wide")
    
    # Sidebar filters
    st.sidebar.header("Filters")
    priority_filter = st.sidebar.selectbox(
        "Priority Level",
        ["All", "High", "Medium", "Low"]
    )
    
    # Main interface
    st.title("Firebase-Powered Election Complaint System")
    
    with st.form("complaint_form"):
        name = st.text_input("Your Name")
        complaint_text = st.text_area("Complaint Details")
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            analysis = analyze_complaint(complaint_text)  # Your existing analysis function
            complaint_data = {
                "timestamp": datetime.now().isoformat(),
                "name": name,
                "text": complaint_text,
                "priority": analysis["priority"],
                "status": "New",
                "analysis": json.dumps(analysis)
            }
            
            complaint_id = save_complaint_to_firebase(complaint_data)
            if complaint_id:
                st.success(f"Complaint #{complaint_id} submitted successfully!")

    # Display complaints
    st.header("Current Complaints")
    df = get_complaints_from_firebase()
    
    if not df.empty:
        # Convert Firebase timestamp
        df['date'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
        
        # Display editable table
        edited_df = st.data_editor(
            df[['date', 'name', 'priority', 'status']],
            column_config={
                "status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["New", "In Progress", "Resolved"]
                )
            },
            key="complaint_editor"
        )
        
        if st.button("Save Changes"):
            for idx, row in edited_df.iterrows():
                updates = {"status": row["status"]}
                update_complaint_in_firebase(idx, updates)
            st.rerun()
    else:
        st.info("No complaints found in database")