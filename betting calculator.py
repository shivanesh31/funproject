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

def calculate_profit(stake, odds, result):
    """Calculate profit/loss based on stake, odds and result"""
    if result == "Win":
        return stake * (odds - 1)
    elif result == "Loss":
        return -stake
    return 0

def load_data(username):
    """Load betting data for specific user"""
    try:
        filename = get_user_file(username)
        if os.path.exists(filename):
            df = pd.read_csv(filename)
            df['Date'] = pd.to_datetime(df['Date'])
            return df
        return pd.DataFrame(columns=[
            'Date', 'Sport', 'Match', 'Bet Type', 'Stake', 'Odds', 'Result', 'Profit/Loss'
        ])
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(columns=[
            'Date', 'Sport', 'Match', 'Bet Type', 'Stake', 'Odds', 'Result', 'Profit/Loss'
        ])

def save_data(df, username):
    """Save betting data for specific user"""
    try:
        filename = get_user_file(username)
        df_to_save = df.copy()
        if not df_to_save.empty:
            df_to_save['Date'] = pd.to_datetime(df_to_save['Date']).dt.strftime('%Y-%m-%d')
        df_to_save.to_csv(filename, index=False)
    except Exception as e:
        st.error(f"Error saving data: {e}")

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
    
    # Initialize session state for storing bets
    if 'bets' not in st.session_state:
        st.session_state.bets = load_data(st.session_state['username'])
    
    # Create tabs for different actions
    tab1, tab2 = st.tabs(["📝 Place New Bet", "🎯 Update Results"])
    
    # Tab 1: Place New Bet
    with tab1:
        with st.form("bet_calculator"):
            col1, col2 = st.columns(2)
            
            with col1:
                date = st.date_input("📅 Date", datetime.now())
                sport = st.selectbox("🏆 Sport", ["Football", "NBA", "NHL", "NFL", "MLB", "NCAAF", "NCAAB", "UFC", 
                                             "Boxing", "Tennis", "Golf", "Cricket", "Rugby", "Darts", "Snooker", 
                                             "Esports", "Other"])
                match = st.text_input("⚔️ Match (e.g., Team A vs Team B)")
                
            with col2:
                bet_type = st.text_input("🎲 Bet Type")
                stake = st.number_input("💵 Stake (RM)", min_value=0.0, step=5.0)
                odds = st.number_input("📊 Odds", min_value=1.01, step=0.05, value=2.00)
            
            # Calculate potential profit
            potential_profit = stake * (odds - 1)
            st.write(f"💫 Potential Profit: RM{potential_profit:.2f}")
            
            submitted = st.form_submit_button("Add Bet")
            
            if submitted:
                if not bet_type:
                    st.error("Please enter a bet type")
                    return
                    
                # Add new bet with Pending status
                new_bet = pd.DataFrame([{
                    'Date': date,
                    'Sport': sport,
                    'Match': match,
                    'Bet Type': bet_type,
                    'Stake': stake,
                    'Odds': odds,
                    'Result': 'Pending',
                    'Profit/Loss': 0
                }])
                
                st.session_state.bets = pd.concat([st.session_state.bets, new_bet], ignore_index=True)
                save_data(st.session_state.bets, st.session_state['username'])
                st.success("✅ Bet added successfully!")
    
    # Tab 2: Update Results
    with tab2:
        st.subheader("🎲 Update Pending Bets")
        
        # Get pending bets
        pending_bets = st.session_state.bets[st.session_state.bets['Result'] == 'Pending']
        
        if pending_bets.empty:
            st.info("📝 No pending bets to update
