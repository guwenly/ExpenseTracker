import streamlit as st
import pandas as pd
from expense_tracker import ExpenseTracker
from database import initialize_database, execute_db_operation
from utils import load_custom_css
from datetime import datetime, date as date_class
from visualizations import create_expense_pie_chart, create_expense_comparison_chart
from auth import login, logout, register, is_authenticated, authentication_required
import logging
import calendar

logging.basicConfig(filename='app.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

st.set_page_config(page_title="Expense Tracker",
                   page_icon="💰",
                   layout="wide",
                   initial_sidebar_state="collapsed")

def load_translations():
    return {
        'English': {
            'Expense Tracker': 'Expense Tracker',
            'Home': 'Home',
            'Monthly Summary': 'Monthly Summary',
            'Compare Expenses': 'Compare Expenses',
            'User Settings': 'User Settings',
            'Sign Out': 'Sign Out',
            'Monthly Salary': 'Monthly Salary',
            'Select Month and Year': 'Select Month and Year',
            'Year': 'Year',
            'Month': 'Month',
            'Salary for': 'Salary for',
            'Update Salary': 'Update Salary',
            'Add Expense': 'Add Expense',
            'Category': 'Category',
            'Amount': 'Amount',
            'Description': 'Description (optional)',
            'Expense Date': 'Expense Date',
            'Expenses': 'Expenses',
            'No expenses recorded for': 'No expenses recorded for',
            'Total Expenses': 'Total Expenses',
            'Remaining Salary': 'Remaining Salary',
            'Currency Settings': 'Currency Settings',
            'Select Currency': 'Select Currency',
            'Language Settings': 'Language Settings',
            'Select Language': 'Select Language',
            'Category Management': 'Category Management',
            'Enter new category name': 'Enter new category name',
            'Add Category': 'Add Category',
            'Select category to remove': 'Select category to remove',
            'Remove Category': 'Remove Category',
            'Total Expenses by Category for': 'Total Expenses by Category for',
            'No salary information available for this month':
            'No salary information available for this month',
            'Welcome to Expense Tracker': 'Welcome to Expense Tracker',
            'Login': 'Login',
            'Register': 'Register',
            'Logged in as': 'Logged in as',
            'Expense Distribution': 'Expense Distribution',
            'Expense Comparison Data': 'Expense Comparison Data',
            'Remove Expense': 'Remove Expense',
        },
        'Turkish': {
            'Expense Tracker': 'Gider Takibi',
            'Home': 'Ana Sayfa',
            'Monthly Summary': 'Aylık Özet',
            'Compare Expenses': 'Giderleri Karşılaştır',
            'User Settings': 'Kullanıcı Ayarları',
            'Sign Out': 'Çıkış Yap',
            'Monthly Salary': 'Aylık Maaş',
            'Select Month and Year': 'Ay ve Yıl Seçin',
            'Year': 'Yıl',
            'Month': 'Ay',
            'Salary for': 'Maaş',
            'Update Salary': 'Maaşı Güncelle',
            'Add Expense': 'Gider Ekle',
            'Category': 'Kategori',
            'Amount': 'Miktar',
            'Description': 'Açıklama (isteğe bağlı)',
            'Expense Date': 'Gider Tarihi',
            'Expenses': 'Giderler',
            'No expenses recorded for': 'Şu tarih için gider kaydı yok:',
            'Total Expenses': 'Toplam Giderler',
            'Remaining Salary': 'Kalan Maaş',
            'Currency Settings': 'Para Birimi Ayarları',
            'Select Currency': 'Para Birimi Seçin',
            'Language Settings': 'Dil Ayarları',
            'Select Language': 'Dil Seçin',
            'Category Management': 'Kategori Yönetimi',
            'Enter new category name': 'Yeni kategori adı girin',
            'Add Category': 'Kategori Ekle',
            'Select category to remove': 'Kaldırılacak kategoriyi seçin',
            'Remove Category': 'Kategori Kaldır',
            'Total Expenses by Category for':
            'Kategoriye Göre Toplam Giderler:',
            'No salary information available for this month':
            'Bu ay için maaş bilgisi mevcut değil',
            'Welcome to Expense Tracker': 'Gider Takibine Hoş Geldiniz',
            'Login': 'Giriş',
            'Register': 'Kayıt Ol',
            'Logged in as': 'Giriş yapıldı:',
            'Expense Distribution': 'Gider Dağılımı',
            'Expense Comparison Data': 'Gider Karşılaştırma Verileri',
            'Remove Expense': 'Gideri Kaldır',
        }
    }

def translate_month(month_name, lang):
    months_tr = {
        'January': 'Ocak',
        'February': 'Şubat',
        'March': 'Mart',
        'April': 'Nisan',
        'May': 'Mayıs',
        'June': 'Haziran',
        'July': 'Temmuz',
        'August': 'Ağustos',
        'September': 'Eylül',
        'October': 'Ekim',
        'November': 'Kasım',
        'December': 'Aralık'
    }
    return months_tr.get(month_name,
                         month_name) if lang == 'Turkish' else month_name

@authentication_required
def show_expense_tracker():
    expense_tracker = ExpenseTracker(st.session_state.user_id)
    translations = load_translations()
    lang = st.session_state.get('language', 'English')
    currency = st.session_state.get('currency', 'USD')

    if 'selected_month' not in st.session_state:
        st.session_state.selected_month = datetime.now().month - 1
    if 'selected_year' not in st.session_state:
        st.session_state.selected_year = datetime.now().year

    st.title(translations[lang]['Expense Tracker'])

    menu = [
        "Home", "Monthly Summary", "Compare Expenses", "User Settings",
        "Sign Out"
    ]
    cols = st.columns(len(menu))
    for idx, item in enumerate(menu):
        if cols[idx].button(translations[lang][item],
                            key=f"menu_{item}",
                            use_container_width=True):
            if item == "Sign Out":
                logout()
                st.rerun()
            else:
                st.session_state.current_page = item.lower().replace(" ", "_")

    if 'current_page' not in st.session_state:
        st.session_state.current_page = "home"

    if st.session_state.current_page == "home":
        show_dashboard(expense_tracker, translations, lang, currency)
    elif st.session_state.current_page == "monthly_summary":
        show_expense_summary(expense_tracker, translations, lang, currency)
    elif st.session_state.current_page == "compare_expenses":
        show_expense_comparison(expense_tracker, translations, lang, currency)
    elif st.session_state.current_page == "user_settings":
        show_settings(expense_tracker, translations, lang, currency)

def show_dashboard(expense_tracker, translations, lang, currency):
    with st.expander(translations[lang]["Select Month and Year"],
                     expanded=True):
        current_year = datetime.now().year
        years = list(range(current_year - 5, current_year + 1))
        months = [
            "January", "February", "March", "April", "May", "June", "July",
            "August", "September", "October", "November", "December"
        ]
        translated_months = [translate_month(month, lang) for month in months]

        col1, col2 = st.columns(2)
        with col1:
            selected_year = st.selectbox(translations[lang]["Year"],
                                         years,
                                         index=years.index(
                                             st.session_state.selected_year))
        with col2:
            selected_month = st.selectbox(
                translations[lang]["Month"],
                translated_months,
                index=st.session_state.selected_month)

    if selected_year != st.session_state.selected_year or selected_month != translated_months[
            st.session_state.selected_month]:
        st.session_state.selected_year = selected_year
        st.session_state.selected_month = translated_months.index(
            selected_month)
        st.rerun()

    selected_month_num = months.index(
        months[st.session_state.selected_month]) + 1

    with st.expander(translations[lang]["Monthly Salary"], expanded=True):
        current_salary = expense_tracker.get_salary(selected_month_num,
                                                    selected_year)
        salary = st.number_input(
            f"{translations[lang]['Salary for']} {translate_month(months[selected_month_num-1], lang)} {selected_year}",
            min_value=0.0,
            step=100.0,
            value=float(current_salary) if current_salary is not None else 0.0)
        if st.button(translations[lang]["Update Salary"]):
            try:
                updated_salary = expense_tracker.update_salary(
                    salary, selected_month_num, selected_year)
                if updated_salary is not None:
                    st.success(
                        f"{translations[lang]['Salary for']} {translate_month(months[selected_month_num-1], lang)} {selected_year} {translations[lang]['Update Salary']} {get_currency_symbol(currency)}{updated_salary:.2f}!"
                    )
                else:
                    st.error("Failed to update salary. Please try again.")
                st.rerun()
            except Exception as e:
                st.error(
                    f"An error occurred while updating the salary: {str(e)}")

    with st.expander(translations[lang]["Add Expense"], expanded=True):
        categories = expense_tracker.get_categories()
        category = st.selectbox(translations[lang]["Category"],
                                options=categories)

        amount = st.number_input(translations[lang]["Amount"],
                                 min_value=0.0,
                                 step=0.01)
        description = st.text_input(translations[lang]["Description"])
        
        min_date = date_class(selected_year, selected_month_num, 1)
        max_date = date_class(selected_year, selected_month_num, 1) + pd.offsets.MonthEnd(0)
        default_date = date_class.today() if date_class.today().year == selected_year and date_class.today().month == selected_month_num else max_date
        expense_date = st.date_input(translations[lang]["Expense Date"], 
                                     value=default_date, 
                                     min_value=min_date, 
                                     max_value=max_date)
        
        if st.button(translations[lang]["Add Expense"]):
            success, message = expense_tracker.add_expense(category, amount, description, expense_date)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    show_category_totals(expense_tracker, selected_month_num, selected_year,
                         salary, translations, lang, currency)

    st.subheader(translations[lang]["Expenses"])
    expenses_df = expense_tracker.get_expenses(selected_month_num,
                                               selected_year)
    if not expenses_df.empty:
        expenses_df['date'] = pd.to_datetime(expenses_df['date'])
        expenses_df['created_at'] = pd.to_datetime(expenses_df['created_at'])
        expenses_df = expenses_df.sort_values('date', ascending=False)

        for date, group in expenses_df.groupby(expenses_df['date'].dt.date,
                                               sort=False):
            day_expenses = group.sort_values(
                'created_at',
                ascending=False)
            st.write(f"**{date.strftime('%Y-%m-%d')}**")

            for _, row in day_expenses.iterrows():
                with st.expander(
                        f"{row['category']} - {get_currency_symbol(currency)}{row['amount']:.2f}"
                ):
                    st.write(
                        f"{translations[lang]['Description']}: {row['description']}"
                    )
                    if st.button(translations[lang]["Remove Expense"],
                                 key=f"remove_{row['id']}"):
                        success, message = expense_tracker.remove_expense(
                            row['id'])
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)

    else:
        st.info(
            f"{translations[lang]['No expenses recorded for']} {translate_month(months[selected_month_num-1], lang)} {selected_year}."
        )

def show_expense_summary(expense_tracker, translations, lang, currency):
    st.title(translations[lang]["Monthly Summary"])

    current_year = datetime.now().year
    years = list(range(current_year - 5, current_year + 1))
    selected_year = st.selectbox(translations[lang]["Year"], years, index=5)
    months = [
        "January", "February", "March", "April", "May", "June", "July",
        "August", "September", "October", "November", "December"
    ]
    translated_months = [translate_month(month, lang) for month in months]
    selected_month = st.selectbox(translations[lang]["Month"],
                                  translated_months,
                                  index=datetime.now().month - 1)
    selected_month_num = months.index(
        months[translated_months.index(selected_month)]) + 1

    salary = expense_tracker.get_salary(selected_month_num, selected_year)
    expenses_df = expense_tracker.get_expenses(selected_month_num,
                                               selected_year)

    if not expenses_df.empty:
        st.subheader(
            f"{translations[lang]['Expenses']} {translate_month(months[selected_month_num-1], lang)} {selected_year}"
        )
        st.dataframe(expenses_df)
        total_expenses = expenses_df['amount'].sum()
        if salary is not None:
            remaining_salary = salary - total_expenses
            st.info(
                f"{translations[lang]['Total Expenses']}: {get_currency_symbol(currency)}{float(total_expenses):.2f}"
            )
            st.success(
                f"{translations[lang]['Remaining Salary']}: {get_currency_symbol(currency)}{float(remaining_salary):.2f}"
            )
        else:
            st.info(
                f"{translations[lang]['Total Expenses']}: {get_currency_symbol(currency)}{float(total_expenses):.2f}"
            )
            st.warning(translations[lang]
                       ["No salary information available for this month"])

        st.subheader(translations[lang]["Expense Distribution"])
        fig = create_expense_pie_chart(expenses_df,
                                       get_currency_symbol(currency), lang)
        st.plotly_chart(fig)
    else:
        st.info(
            f"{translations[lang]['No expenses recorded for']} {translate_month(months[selected_month_num-1], lang)} {selected_year}."
        )
        if salary is not None:
            st.success(
                f"{translations[lang]['Remaining Salary']}: {get_currency_symbol(currency)}{float(salary):.2f}"
            )
        else:
            st.warning(translations[lang]
                       ["No salary information available for this month"])

def show_expense_comparison(expense_tracker, translations, lang, currency):
    st.title(translations[lang]["Compare Expenses"])

    current_year = datetime.now().year
    years = list(range(current_year - 5, current_year + 1))
    months = [
        "January", "February", "March", "April", "May", "June", "July",
        "August", "September", "October", "November", "December"
    ]
    translated_months = [translate_month(month, lang) for month in months]

    selected_years = st.multiselect(translations[lang]["Year"],
                                    years,
                                    default=[current_year])
    selected_months = st.multiselect(
        translations[lang]["Month"],
        translated_months,
        default=[translated_months[datetime.now().month - 1]])

    selected_month_nums = [
        months.index(months[translated_months.index(month)]) + 1
        for month in selected_months
    ]

    if selected_years and selected_months:
        comparison_data = []
        for year in selected_years:
            for month_num in selected_month_nums:
                expenses_df = expense_tracker.get_expenses(month_num, year)
                if not expenses_df.empty:
                    total_expenses = expenses_df['amount'].sum()
                    comparison_data.append({
                        'year':
                        year,
                        'month':
                        translate_month(months[month_num - 1], lang),
                        'total_expenses':
                        float(total_expenses)
                    })

        if comparison_data:
            comparison_df = pd.DataFrame(comparison_data)
            fig = create_expense_comparison_chart(
                comparison_df, get_currency_symbol(currency), lang)
            st.plotly_chart(fig)

            st.subheader(translations[lang]["Expense Comparison Data"])
            st.dataframe(comparison_df)
        else:
            st.info("No data available for the selected months and years.")
    else:
        st.info(
            "Please select at least one month and one year to compare expenses."
        )

def show_settings(expense_tracker, translations, lang, currency):
    st.title(translations[lang]["User Settings"])

    st.subheader(translations[lang]["Currency Settings"])
    currency_options = ["USD", "TRY"]
    selected_currency = st.selectbox(
        translations[lang]["Select Currency"],
        options=currency_options,
        index=currency_options.index(st.session_state.get('currency', 'USD')))
    if selected_currency != st.session_state.get('currency', 'USD'):
        st.session_state.currency = selected_currency
        st.success(
            f"{translations[lang]['Currency Settings']} {selected_currency}")

    st.subheader(translations[lang]["Language Settings"])
    language_options = ["English", "Turkish"]
    selected_language = st.selectbox(translations[lang]["Select Language"],
                                     options=language_options,
                                     index=language_options.index(
                                         st.session_state.get(
                                             'language', 'English')))
    if selected_language != st.session_state.get('language', 'English'):
        st.session_state.language = selected_language
        st.success(
            f"{translations[lang]['Language Settings']} {selected_language}")

    st.subheader(translations[lang]["Category Management"])
    col1, col2 = st.columns(2)

    with col1:
        new_category = st.text_input(
            translations[lang]["Enter new category name"])
        if st.button(translations[lang]["Add Category"]):
            success, message = expense_tracker.add_category(new_category)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    with col2:
        categories = expense_tracker.get_categories()
        category_to_remove = st.selectbox(
            translations[lang]["Select category to remove"],
            options=categories)
        if st.button(translations[lang]["Remove Category"]):
            success, message = expense_tracker.remove_category(
                category_to_remove)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

def show_category_totals(expense_tracker, month, year, salary, translations,
                         lang, currency):
    expenses_df = expense_tracker.get_expenses(month, year)
    if not expenses_df.empty:
        category_totals = expenses_df.groupby(
            'category')['amount'].sum().sort_values(ascending=False)
        st.subheader(
            f"{translations[lang]['Total Expenses by Category for']} {translate_month(date_class(year, month, 1).strftime('%B'), lang)} {year}"
        )
        for category, total in category_totals.items():
            st.text(f"{category}: {get_currency_symbol(currency)}{total:.2f}")

        total_expenses = float(expenses_df['amount'].sum())
        if salary is not None and salary > 0:
            remaining_salary = float(salary) - total_expenses
            st.info(
                f"{translations[lang]['Total Expenses']}: {get_currency_symbol(currency)}{total_expenses:.2f}"
            )
            st.success(
                f"{translations[lang]['Remaining Salary']}: {get_currency_symbol(currency)}{remaining_salary:.2f}"
            )
        else:
            st.info(
                f"{translations[lang]['Total Expenses']}: {get_currency_symbol(currency)}{total_expenses:.2f}"
            )
            st.warning(translations[lang]
                       ["No salary information available for this month"])
    else:
        if salary is not None and salary > 0:
            st.info(
                f"{translations[lang]['No expenses recorded for']} {translate_month(date_class(year, month, 1).strftime('%B'), lang)} {year}."
            )
            st.success(
                f"{translations[lang]['Remaining Salary']}: {get_currency_symbol(currency)}{float(salary):.2f}"
            )
        else:
            st.info(
                f"{translations[lang]['No expenses recorded for']} {translate_month(date_class(year, month, 1).strftime('%B'), lang)} {year}."
            )
            st.warning(translations[lang]
                       ["No salary information available for this month"])

def get_currency_symbol(currency):
    return '₺' if currency == 'TRY' else '$'

def main():
    load_custom_css()
    translations = load_translations()

    token = st.query_params.get('jwt_token')
    if token:
        st.session_state.token = token
        st.query_params.clear()

    if is_authenticated():
        st.success(
            f"{translations[st.session_state.get('language', 'English')]['Logged in as']} {st.session_state.user.lower()}"
        )
        show_expense_tracker()
    else:
        st.title(translations[st.session_state.get(
            'language', 'English')]["Welcome to Expense Tracker"])
        tab1, tab2 = st.tabs([
            translations[st.session_state.get('language', 'English')]["Login"],
            translations[st.session_state.get('language',
                                              'English')]["Register"]
        ])

        with tab1:
            if login():
                st.rerun()

        with tab2:
            register()

    st.write("""
    <script>
    document.addEventListener('DOMContentLoaded', (event) => {
        const token = sessionStorage.getItem('jwt_token');
        if (token) {
            const currentUrl = new URL(window.location.href);
            currentUrl.searchParams.set('jwt_token', token);
            window.history.replaceState({}, '', currentUrl);
            window.location.reload();
        }
    });
    </script>
    """,
             unsafe_allow_html=True)

if __name__ == "__main__":
    logging.info("Starting application")
    initialize_database()
    logging.info("Database initialized")
    print("Database initialization completed.")
    main()