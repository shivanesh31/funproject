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
    
    st.title("💰 Shivanesh Betting Profit Calculator 💸")
    
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
                with st.expander(f"🎯 {bet['Match']} - {bet['Date']} ({bet['Sport']})"):
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
                            st.success("Updated as Win!")
                            st.rerun()
                    
                    with col2:
                        if st.button("❌ Loss", key=f"loss_{idx}"):
                            st.session_state.bets.loc[idx, 'Result'] = 'Loss'
                            st.session_state.bets.loc[idx, 'Profit/Loss'] = calculate_profit(
                                bet['Stake'], bet['Odds'], 'Loss'
                            )
                            st.success("Updated as Loss!")
                            st.rerun()
    
    # Display Summary Statistics
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
    
    # Display all bets
    st.header("📚 All Bets History")
    st.dataframe(
        st.session_state.bets.sort_values('Date', ascending=False),
        use_container_width=True
    )
    
    # Add export capability
    if st.button("📥 Export to CSV"):
        st.session_state.bets.to_csv("betting_history.csv", index=False)
        st.success("✅ Data exported to betting_history.csv!")

if __name__ == "__main__":
    main()
