import streamlit as st
import pandas as pd
from datetime import datetime
import os
import hashlib
import json

def make_hashed_password(password):
    """Create hashed password"""
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_password(password, hashed_password):
    """Verify password"""
    return make_hashed_password(password) == hashed_password

def load_users():
    """Load user data"""
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save user data"""
    with open('users.json', 'w') as f:
        json.dump(users, f)

def get_user_file(username):
    """Get filename for user's betting data"""
    return f'betting_data_{username}.csv'

def load_data(username):
    """Load betting data for specific user"""
    filename = get_user_file(username)
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    return pd.DataFrame(columns=[
        'Date', 'Sport', 'Match', 'Bet Type', 'Stake', 'Odds', 'Result', 'Profit/Loss'
    ])

def save_data(df, username):
    """Save betting data for specific user"""
    filename = get_user_file(username)
    df_to_save = df.copy()
    if not df_to_save.empty:
        df_to_save['Date'] = pd.to_datetime(df_to_save['Date']).dt.strftime('%Y-%m-%d')
    df_to_save.to_csv(filename, index=False)

def login_page():
    """Handle login and registration"""
    st.title("💰 Betting Tracker Login")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                users = load_users()
                if username in users and check_password(password, users[username]):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("Choose Username")
            new_password = st.text_input("Choose Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Register")
            
            if submitted:
                if new_password != confirm_password:
                    st.error("Passwords don't match")
                    return
                
                users = load_users()
                if new_username in users:
                    st.error("Username already exists")
                    return
                
                users[new_username] = make_hashed_password(new_password)
                save_users(users)
                st.success("Registration successful! Please login.")

[Previous betting calculator code remains the same, but with these modifications:
1. Replace all save_data() calls with save_data(df, st.session_state['username'])
2. Replace all load_data() calls with load_data(st.session_state['username'])
3. Add logout button in the main interface
4. Add username display in the title]

def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        login_page()
        return

    # Add logout button
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = None
        st.rerun()

    st.title(f"💰 Betting Tracker - {st.session_state['username']} 💸")
    
    [Rest of the previous main() function code]

if __name__ == "__main__":
    main()
