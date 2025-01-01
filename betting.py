import streamlit as st
import pandas as pd
from datetime import datetime
import os

def calculate_profit(stake, odds, result):
    """Calculate profit/loss based on stake, odds and result"""
    if result == "Win":
        return stake * (odds - 1)
    elif result == "Loss":
        return -stake
    return 0

def load_data():
    """Load betting data from CSV file"""
    try:
        if os.path.exists('betting_data.csv'):
            df = pd.read_csv('betting_data.csv')
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

def save_data(df):
    """Save betting data to CSV file"""
    try:
        df_to_save = df.copy()
        if not df_to_save.empty:
            df_to_save['Date'] = pd.to_datetime(df_to_save['Date']).dt.strftime('%Y-%m-%d')
        df_to_save.to_csv('betting_data.csv', index=False)
    except Exception as e:
        st.error(f"Error saving data: {e}")

def main():
    st.set_page_config(page_title="Betting Profit Calculator", layout="wide")
    
    # Initialize session state for storing bets
    if 'bets' not in st.session_state:
        st.session_state.bets = load_data()
        
     if 'confirm_delete' not in st.session_state:
        st.session_state.confirm_delete = None
         
    st.title("💰 Shivanesh Betting Profit Calculator 💸")
    
    # Create tabs for different actions
     tab1, tab2, tab3 = st.tabs(["📝 Place New Bet", "🎯 Update Results", "🗑️ Manage Bets"])
    
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
                save_data(st.session_state.bets)
                st.success("✅ Bet added successfully!")
    
    # Tab 2: Update Results
    with tab2:
        st.subheader("🎲 Update Pending Bets")
        
        # Get pending bets
        pending_bets = st.session_state.bets[st.session_state.bets['Result'] == 'Pending']
        
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
                            st.session_state.bets.loc[idx, 'Result'] = 'Win'
                            st.session_state.bets.loc[idx, 'Profit/Loss'] = calculate_profit(
                                bet['Stake'], bet['Odds'], 'Win'
                            )
                            save_data(st.session_state.bets)
                            st.success("Updated as Win!")
                            st.rerun()
                    
                    with col2:
                        if st.button("❌ Loss", key=f"loss_{idx}"):
                            st.session_state.bets.loc[idx, 'Result'] = 'Loss'
                            st.session_state.bets.loc[idx, 'Profit/Loss'] = calculate_profit(
                                bet['Stake'], bet['Odds'], 'Loss'
                            )
                            save_data(st.session_state.bets)
                            st.success("Updated as Loss!")
                            st.rerun()
     with tab3:
        st.subheader("🗑️ Delete Bets")
        
        if st.session_state.bets.empty:
            st.info("No bets to manage")
        else:
            # Display all bets with delete buttons
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
                                st.session_state.bets = st.session_state.bets.drop(idx)
                                save_data(st.session_state.bets, st.session_state['username'])
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

    # [Previous summary statistics and display code remains the same]

if __name__ == "__main__":
    main()
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
            backup_filename = f"betting_history_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df_to_save = st.session_state.bets.copy()
            df_to_save['Date'] = pd.to_datetime(df_to_save['Date']).dt.strftime('%Y-%m-%d')
            df_to_save.to_csv(backup_filename, index=False)
            st.success(f"✅ Data backed up to {backup_filename}!")

if __name__ == "__main__":
    main()
