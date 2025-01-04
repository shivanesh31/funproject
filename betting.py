import streamlit as st
import pandas as pd
from datetime import datetime
import os
import hashlib
import json

# Helper Functions
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

def get_user_bankroll(username):
    """Load user's bankroll data"""
    try:
        if os.path.exists('bankroll.json'):
            with open('bankroll.json', 'r') as f:
                bankrolls = json.load(f)
                return bankrolls.get(username, 0)
        return 0
    except Exception:
        return 0

def save_user_bankroll(username, amount):
    """Save user's bankroll data"""
    try:
        bankrolls = {}
        if os.path.exists('bankroll.json'):
            with open('bankroll.json', 'r') as f:
                bankrolls = json.load(f)
        bankrolls[username] = amount
        with open('bankroll.json', 'w') as f:
            json.dump(bankrolls, f)
    except Exception as e:
        st.error(f"Error saving bankroll: {e}")

# Login Page Function
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
            initial_bankroll = st.number_input("Initial Bankroll (RM)", min_value=0.0, step=100.0)
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
                save_user_bankroll(new_username, initial_bankroll)
                st.success("Registration successful! Please login.")

# Main Application Function
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
    
        # Initialize session state for storing bets
        if 'bets' not in st.session_state:
            st.session_state.bets = load_data(st.session_state['username'])
        
        # Initialize bankroll
        if 'bankroll' not in st.session_state:
            st.session_state.bankroll = get_user_bankroll(st.session_state['username'])
        
        if 'confirm_delete' not in st.session_state:
            st.session_state.confirm_delete = None
    
        st.title(f"💰 Betting Tracker - {st.session_state['username']} 💸")
    
        # Bankroll Management in Sidebar
        st.sidebar.markdown("---")
        st.sidebar.header("💰 Bankroll Management")
        
        # Add/Remove funds
        with st.sidebar.expander("Manage Funds"):
            action = st.radio("Action", ["Add Funds", "Remove Funds"])
            amount = st.number_input("Amount (RM)", min_value=0.0, step=10.0)
            if st.button("Update Bankroll"):
                if action == "Add Funds":
                    st.session_state.bankroll += amount
                else:
                    if amount > st.session_state.bankroll:
                        st.error("Insufficient funds!")
                    else:
                        st.session_state.bankroll -= amount
                save_user_bankroll(st.session_state['username'], st.session_state.bankroll)
                st.success(f"Bankroll updated! New balance: RM{st.session_state.bankroll:.2f}")
                st.rerun()
    
        # Calculate available balance
        pending_bets = st.session_state.bets[st.session_state.bets['Result'] == 'Pending']
        pending_stakes = pending_bets['Stake'].sum()
        available_balance = st.session_state.bankroll - pending_stakes
    
        # Display balances
        st.sidebar.metric("Current Bankroll", f"RM{st.session_state.bankroll:.2f}")
        st.sidebar.metric("Available Balance", 
                         f"RM{available_balance:.2f}",
                         help="Current bankroll minus pending bet stakes")
        
        if pending_stakes > 0:
            st.sidebar.write(f"🎲 Amount in pending bets: RM{pending_stakes:.2f}")
        
        # Create tabs for different actions
        tab1, tab2, tab3 = st.tabs(["📝 Place New Bet", "🎯 Update Results", "🗑️ Manage Bets"])
        
       # Add this code in the "Place New Bet" tab section, replace or modify the existing form:
    
        # Tab 1: Place New Bet
        with tab1:
            bet_type_choice = st.radio("Select Bet Type", ["Single", "Parlay"])
            
            if bet_type_choice == "Single":
                with st.form("single_bet_calculator"):
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
                    
                    potential_profit = stake * (odds - 1)
                    st.write(f"💫 Potential Profit: RM{potential_profit:.2f}")
                    
                    submitted = st.form_submit_button("Add Single Bet")
                    
                    if submitted:
                        if not bet_type:
                            st.error("Please enter a bet type")
                            return
                        
                        if stake > available_balance:
                            st.error("Insufficient available balance!")
                            return
                            
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
            
          # First, initialize parlay session state if not exists
    
    
    # In your Tab 1, replace the parlay section with:
    
                else:  # Parlay bet
                with st.form("parlay_bet_calculator"):
                    date = st.date_input("📅 Date", datetime.now())
                    
                    # Control number of picks
                    col1, col2, col3 = st.columns([2,1,1])
                    with col1:
                        st.write("Number of Picks:")
                    with col2:
                        if st.form_submit_button("-"):
                            if st.session_state.num_parlay_picks > 2:
                                st.session_state.num_parlay_picks -= 1
                                st.rerun()
                    with col3:
                        if st.form_submit_button("+"):
                            if st.session_state.num_parlay_picks < 10:
                                st.session_state.num_parlay_picks += 1
                                st.rerun()
                    
                    st.write(f"Current picks: {st.session_state.num_parlay_picks}")
                    st.markdown("---")
                    
                    # Store picks info
                    picks = []
                    total_odds = 1.0
                    
                    # Create input fields for each pick
                    for i in range(st.session_state.num_parlay_picks):
                        st.markdown(f"### Pick {i+1}")
                        pick_col1, pick_col2 = st.columns(2)
                        
                        pick = {}
                        with pick_col1:
                            pick['Sport'] = st.selectbox(
                                "Sport",
                                ["Football", "NBA", "NHL", "NFL", "MLB", "NCAAF", "NCAAB", "UFC", 
                                 "Boxing", "Tennis", "Golf", "Cricket", "Rugby", "Darts", "Snooker", 
                                 "Esports", "Other"],
                                key=f"sport_{i}"
                            )
                            pick['Match'] = st.text_input("Match", key=f"match_{i}")
                        
                        with pick_col2:
                            pick['Bet Type'] = st.text_input("Bet Type", key=f"bet_{i}")
                            pick['Odds'] = st.number_input(
                                "Odds",
                                min_value=1.01,
                                step=0.05,
                                value=2.00,
                                key=f"odds_{i}"
                            )
                        
                        picks.append(pick)
                        total_odds *= pick['Odds']
                        st.markdown("---")
                    
                    # Stake and calculations
                    stake = st.number_input("Total Stake (RM)", min_value=0.0, step=5.0)
                    potential_profit = stake * (total_odds - 1)
                    
                    # Summary
                    st.markdown("### Parlay Summary")
                    for i, pick in enumerate(picks):
                        st.write(f"Pick {i+1}: {pick['Sport']} - {pick['Match']} - {pick['Bet Type']} @ {pick['Odds']:.2f}")
                    
                    st.markdown("### Total")
                    st.write(f"Combined Odds: {total_odds:.2f}")
                    st.write(f"Potential Profit: RM{potential_profit:.2f}")
                    
                    # Submit button
                    submitted = st.form_submit_button("Add Parlay")
                    
                    if submitted:
                        # Validate inputs
                        if any(not pick['Match'] or not pick['Bet Type'] for pick in picks):
                            st.error("Please fill in all match and bet type information")
                            return
                        
                        if stake > available_balance:
                            st.error("Insufficient available balance!")
                            return
                        
                        # Create parlay description
                        parlay_description = " | ".join(
                            [f"{p['Sport']}: {p['Match']} ({p['Bet Type']})" for p in picks]
                        )
                        
                        # Add to bets
                        new_bet = pd.DataFrame([{
                            'Date': date,
                            'Sport': "Parlay",
                            'Match': parlay_description,
                            'Bet Type': f"{st.session_state.num_parlay_picks}-Pick Parlay",
                            'Stake': stake,
                            'Odds': total_odds,
                            'Result': 'Pending',
                            'Profit/Loss': 0
                        }])
                        
                        st.session_state.bets = pd.concat([st.session_state.bets, new_bet], ignore_index=True)
                        save_data(st.session_state.bets, st.session_state['username'])
                        st.success("✅ Parlay added successfully!")

# Tab 2: Update Results
    with tab2:
        st.subheader("🎲 Update Pending Bets")
        
        # Get pending bets
        if pending_bets.empty:
            st.info("📝 No pending bets to update")
        else:
            for idx, bet in pending_bets.iterrows():
                with st.expander(f"🎯 {bet['Match']} - {bet['Date'].strftime('%Y-%m-%d')} ({bet['Sport']})"):
                    st.write(f"🎲 Bet Type: {bet['Bet Type']}")
                    st.write(f"💵 Stake: RM{bet['Stake']:.2f}")
                    st.write(f"📊 Odds: {bet['Odds']:.2f}")
                    st.write(f"💫 Potential Profit: RM{(bet['Stake'] * (bet['Odds'] - 1)):.2f}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🎉 Win", key=f"win_{idx}"):
                            profit = calculate_profit(bet['Stake'], bet['Odds'], 'Win')
                            st.session_state.bets.loc[idx, 'Result'] = 'Win'
                            st.session_state.bets.loc[idx, 'Profit/Loss'] = profit
                            st.session_state.bankroll += profit + bet['Stake']  # Return stake plus profit
                            save_data(st.session_state.bets, st.session_state['username'])
                            save_user_bankroll(st.session_state['username'], st.session_state.bankroll)
                            st.success("Updated as Win!")
                            st.rerun()
                    
                    with col2:
                        if st.button("❌ Loss", key=f"loss_{idx}"):
                            st.session_state.bets.loc[idx, 'Result'] = 'Loss'
                            st.session_state.bets.loc[idx, 'Profit/Loss'] = -bet['Stake']
                            save_data(st.session_state.bets, st.session_state['username'])
                            st.success("Updated as Loss!")
                            st.rerun()

    # Tab 3: Manage Bets
    with tab3:
        st.subheader("🗑️ Delete Bets")
        
        if st.session_state.bets.empty:
            st.info("No bets to manage")
        else:
            display_df = st.session_state.bets.copy()
            display_df['Date'] = pd.to_datetime(display_df['Date'])
            display_df = display_df.sort_values('Date', ascending=False)

            for idx, bet in display_df.iterrows():
                with st.expander(f"{bet['Match']} - {bet['Date'].strftime('%Y-%m-%d')} ({bet['Sport']})"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"🎲 Bet Type: {bet['Bet Type']}")
                        st.write(f"💵 Stake: RM{bet['Stake']:.2f}")
                        st.write(f"📊 Odds: {bet['Odds']:.2f}")
                        st.write(f"Result: {bet['Result']}")
                        if bet['Result'] != 'Pending':
                            st.write(f"Profit/Loss: RM{bet['Profit/Loss']:.2f}")
                    
                    with col2:
                        # Two-step deletion process
                        if st.session_state.confirm_delete == idx:
                            if st.button("❗ Confirm Delete", key=f"confirm_{idx}"):
                                if bet['Result'] == 'Pending':
                                    st.session_state.bankroll += bet['Stake']
                                st.session_state.bets = st.session_state.bets.drop(idx)
                                save_data(st.session_state.bets, st.session_state['username'])
                                save_user_bankroll(st.session_state['username'], st.session_state.bankroll)
                                st.session_state.confirm_delete = None
                                st.success("Bet deleted successfully!")
                                st.rerun()
                            if st.button("Cancel", key=f"cancel_{idx}"):
                                st.session_state.confirm_delete = None
                                st.rerun()
                        else:
                            if st.button("🗑️ Delete", key=f"delete_{idx}"):
                                st.session_state.confirm_delete = idx
                                st.rerun()

    # Display Summary Statistics
    if not st.session_state.bets.empty:
        st.header("📈 Summary Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        completed_bets = st.session_state.bets[st.session_state.bets['Result'] != 'Pending']
        total_profit = completed_bets['Profit/Loss'].sum()
        total_stake = completed_bets['Stake'].sum()
        roi = (total_profit / total_stake * 100) if total_stake > 0 else 0
        
        with col1:
            st.metric("🎯 Total Bets", len(st.session_state.bets))
        with col2:
            st.metric("💵 Total Stake", f"RM{total_stake:.2f}")
        with col3:
            st.metric("💰 Total Profit/Loss", f"RM{total_profit:.2f}")
        with col4:
            st.metric("📊 ROI", f"{roi:.1f}%")
        
        # Sport-wise breakdown
        st.subheader("🏆 Sport-wise Performance")
        sport_stats = completed_bets.groupby('Sport').agg({
            'Profit/Loss': 'sum',
            'Result': lambda x: (x == 'Win').sum() / len(x) * 100 if len(x) > 0 else 0
        }).round(2)
        sport_stats.columns = ['Profit/Loss (RM)', 'Win Rate (%)']
        st.dataframe(sport_stats)
        
        # Display all bets with proper date sorting
        st.header("📚 All Bets History")
        display_df = st.session_state.bets.copy()
        display_df['Date'] = pd.to_datetime(display_df['Date'])
        display_df = display_df.sort_values('Date', ascending=False)
        display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
        st.dataframe(display_df, use_container_width=True)
        
        # Add backup capability
        if st.button("📥 Backup Data"):
            backup_filename = f"betting_history_backup_{st.session_state['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df_to_save = st.session_state.bets.copy()
            df_to_save['Date'] = pd.to_datetime(df_to_save['Date']).dt.strftime('%Y-%m-%d')
            df_to_save.to_csv(backup_filename, index=False)
            st.success(f"✅ Data backed up to {backup_filename}!")

    # Add extra space at bottom
    st.markdown("<br>" * 5, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
