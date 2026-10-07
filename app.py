import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta

# Page Configuration for a modern look
st.set_page_config(page_title="Finance Dashboard", page_icon="💰", layout="wide")

# --- 1. MOCK DATA GENERATION ---
# (Ise aap apne actual CSV ya SQL database se replace kar sakte hain)
@st.cache_data
def load_data():
    np.random.seed(42)
    dates = [datetime.today() - timedelta(days=i) for i in range(30)]
    
    # Generate random transactions
    data = pd.DataFrame({
        'Date': np.random.choice(dates, 100),
        'Category': np.random.choice(['Food', 'Rent', 'Transport', 'Entertainment', 'Utilities', 'Salary', 'Freelance'], 100),
        'Type': np.random.choice(['Expense', 'Income'], 100, p=[0.7, 0.3]),
        'Amount': np.random.randint(100, 5000, 100)
    })
    
    # Adjust Income amounts to be higher
    data.loc[data['Type'] == 'Income', 'Amount'] = data['Amount'] * 3
    return data.sort_values('Date')

df = load_data()

# --- 2. SIDEBAR FILTERS ---
st.sidebar.header("Dashboard Filters ⚙️")
selected_type = st.sidebar.multiselect("Select Transaction Type", df['Type'].unique(), default=df['Type'].unique())
selected_category = st.sidebar.multiselect("Select Category", df['Category'].unique(), default=df['Category'].unique())

# Filter dataset based on sidebar
filtered_df = df[(df['Type'].isin(selected_type)) & (df['Category'].isin(selected_category))]

# --- 3. MAIN DASHBOARD UI ---
st.title("📊 Personal Finance Dashboard")
st.markdown("Monitor your income, expenses, and savings at a glance.")
st.divider()

# Top KPIs
total_income = filtered_df[filtered_df['Type'] == 'Income']['Amount'].sum()
total_expense = filtered_df[filtered_df['Type'] == 'Expense']['Amount'].sum()
savings = total_income - total_expense

col1, col2, col3 = st.columns(3)
col1.metric("Total Income", f"₹{total_income:,.2f}", "📈")
col2.metric("Total Expense", f"₹{total_expense:,.2f}", "-📉")
col3.metric("Net Savings", f"₹{savings:,.2f}", f"{'+' if savings > 0 else '-'}💰")

st.divider()

# --- 4. VISUALIZATIONS ---
col_charts1, col_charts2 = st.columns(2)

with col_charts1:
    st.subheader("Expenses by Category")
    expense_data = filtered_df[filtered_df['Type'] == 'Expense']
    if not expense_data.empty:
        fig_pie = px.pie(expense_data, values='Amount', names='Category', hole=0.4, 
                         color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No expense data available for selected filters.")

with col_charts2:
    st.subheader("Cash Flow Over Time")
    # Group by Date and Type
    timeline_data = filtered_df.groupby([filtered_df['Date'].dt.date, 'Type'])['Amount'].sum().reset_index()
    if not timeline_data.empty:
        fig_line = px.bar(timeline_data, x='Date', y='Amount', color='Type', barmode='group',
                          color_discrete_map={'Income': '#00CC96', 'Expense': '#EF553B'})
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("No timeline data available.")

# --- 5. RECENT TRANSACTIONS TABLE ---
st.subheader("📝 Recent Transactions")
st.dataframe(
    filtered_df.sort_values(by='Date', ascending=False).head(10).style.format({'Amount': '₹{:.2f}'}),
    use_container_width=True,
    hide_index=True
)