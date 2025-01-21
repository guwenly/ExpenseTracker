import streamlit as st
from expense_tracker import ExpenseTracker
from visualizations import create_expense_pie_chart
from datetime import datetime, date
from auth import authentication_required

@authentication_required
def show_expense_summary():
    st.title("Expense Summary")
    expense_tracker = ExpenseTracker(st.session_state.user_id)

    current_year = datetime.now().year
    years = list(range(current_year - 5, current_year + 1))
    selected_year = st.selectbox("Year", years, index=5)
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    selected_month = st.selectbox("Month", months, index=datetime.now().month - 1)
    selected_month_num = months.index(selected_month) + 1
    
    salary = expense_tracker.get_salary(selected_month_num, selected_year)
    expenses_df = expense_tracker.get_expenses(selected_month_num, selected_year)
    
    if not expenses_df.empty:
        st.subheader(f"Expenses for {selected_month} {selected_year}")
        st.dataframe(expenses_df)
        total_expenses = expenses_df['amount'].sum()
        remaining_salary = salary - total_expenses
        st.info(f"Total Expenses: ${float(total_expenses):.2f}")
        st.success(f"Remaining Salary: ${float(remaining_salary):.2f}")

        st.subheader("Expense Distribution")
        fig = create_expense_pie_chart(expenses_df)
        st.plotly_chart(fig)
    else:
        st.info(f"No expenses recorded for {selected_month} {selected_year}.")
        st.success(f"Remaining Salary: ${float(salary):.2f}")

if __name__ == "__main__":
    show_expense_summary()
