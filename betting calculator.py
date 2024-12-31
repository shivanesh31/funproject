import streamlit as st
import pandas as pd
from datetime import datetime

def calculate_profit(stake, odds, result):
    """Calculate profit/loss based on stake, odds and result"""
    if result == "Win":
        return stake * (odds - 1)
    elif result == "Loss":
        return -stake
    return 0

def main():
    st.set_page_config(page_title="Betting Profit Calculator", layout="wide")
    
    # Initialize session state for storing bets
    if 'bets' not in st.session_state:
        st.session_state.bets = pd.DataFrame(columns=[
            'Date', 'Sport', 'Match', 'Bet Type', 'Stake', 'Odds', 'Result', 'Profit/Loss'
        ])
    
    st.title("Betting Profit Calculator")
    
    # Input form
    with st.form("bet_calculator"):
        col1, col2 = st.columns(2)
        
        with col1:
            date = st.date_input("Date", datetime.now())
            sport = st.selectbox("Sport", ["Football", "NBA", "NHL"])
            match = st.text_input("Match (e.g., Team A vs Team B)")
            
        with col2:
            bet_types = {
                "Football": ["BTTS", "Home W", "Away W", "o2.5", "u2.5", "DNB"],
                "NBA": ["Money Line", "Spread", "Over/Under", "Player Props"],
                "NHL": ["Money Line", "Puck Line", "Over/Under"]
            }
            bet_type = st.selectbox("Bet Type", bet_types[sport])
            stake = st.number_input("Stake ($)", min_value=0.0, step=5.0)
            odds = st.number_input("Odds", min_value=1.01, step=0.05, value=2.00)
        
        # Calculate potential profit
        potential_profit = stake * (odds - 1)
        st.write(f"Potential Profit: ${potential_profit:.2f}")
        
        # Add result selection for completed bets
        result = st.selectbox("Result", ["Pending", "Win", "Loss"])
        
        submitted = st.form_submit_button("Add Bet")
        
        if submitted:
            profit = calculate_profit(stake, odds, result) if result != "Pending" else 0
            
            # Add new bet to the dataframe
            new_bet = pd.DataFrame([{
                'Date': date,
                'Sport': sport,
                'Match': match,
                'Bet Type': bet_type,
                'Stake': stake,
                'Odds': odds,
                'Result': result,
                'Profit/Loss': profit
            }])
            
            st.session_state.bets = pd.concat([st.session_state.bets, new_bet], ignore_index=True)
            st.success("Bet added successfully!")
    
    # Display Summary Statistics
    if not st.session_state.bets.empty:
        st.header("Summary Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        completed_bets = st.session_state.bets[st.session_state.bets['Result'] != 'Pending']
        total_profit = completed_bets['Profit/Loss'].sum()
        total_stake = completed_bets['Stake'].sum()
        roi = (total_profit / total_stake * 100) if total_stake > 0 else 0
        
        with col1:
            st.metric("Total Bets", len(st.session_state.bets))
        with col2:
            st.metric("Total Stake", f"${total_stake:.2f}")
        with col3:
            st.metric("Total Profit/Loss", f"${total_profit:.2f}")
        with col4:
            st.metric("ROI", f"{roi:.1f}%")
        
        # Sport-wise breakdown
        st.subheader("Sport-wise Performance")
        sport_stats = completed_bets.groupby('Sport').agg({
            'Profit/Loss': 'sum',
            'Result': lambda x: (x == 'Win').sum() / len(x) * 100 if len(x) > 0 else 0
        }).round(2)
        sport_stats.columns = ['Profit/Loss ($)', 'Win Rate (%)']
        st.dataframe(sport_stats)
        
        # Display all bets
        st.header("All Bets")
        st.dataframe(
            st.session_state.bets.sort_values('Date', ascending=False),
            use_container_width=True
        )
        
        # Add export capability
        if st.button("Export to CSV"):
            st.session_state.bets.to_csv("betting_history.csv", index=False)
            st.success("Data exported to betting_history.csv!")

if __name__ == "__main__":
    main()