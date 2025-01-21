import streamlit as st
import pandas as pd
from expense_tracker import ExpenseTracker
from visualizations import create_category_comparison_chart
from datetime import datetime
from auth import authentication_required

@authentication_required
def show_expense_comparison():
    st.title("Expense Comparison")
    expense_tracker = ExpenseTracker(st.session_state.user_id)

    # Month and year selection
    current_year = datetime.now().year
    years = list(range(current_year - 5, current_year + 1))
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    # Multi-select for months and years
    selected_years = st.multiselect("Select Years", years, default=[current_year])
    selected_months = st.multiselect("Select Months", months, default=[months[datetime.now().month - 1]])

    # Convert selected months to numbers
    selected_month_nums = [months.index(month) + 1 for month in selected_months]

    if selected_years and selected_months:
        comparison_data = []
        for year in selected_years:
            for month_num in selected_month_nums:
                expenses_df = expense_tracker.get_expenses(month_num, year)
                if not expenses_df.empty:
                    grouped_expenses = expenses_df.groupby('category')['amount'].sum().reset_index()
                    for _, row in grouped_expenses.iterrows():
                        comparison_data.append({
                            'year': year,
                            'month': months[month_num - 1],
                            'category': row['category'],
                            'amount': float(row['amount'])
                        })
        
        if comparison_data:
            comparison_df = pd.DataFrame(comparison_data)
            fig = create_category_comparison_chart(comparison_df)
            st.plotly_chart(fig)

            # Display the data in a table format
            st.subheader("Expense Comparison Data")
            pivot_df = comparison_df.pivot_table(
                values='amount', 
                index=['year', 'month'], 
                columns='category', 
                aggfunc='sum', 
                fill_value=0
            ).reset_index()
            st.dataframe(pivot_df)
        else:
            st.info("No data available for the selected months and years.")
    else:
        st.info("Please select at least one month and one year to compare expenses.")

if __name__ == "__main__":
    show_expense_comparison()
