import pandas as pd
from database import execute_db_operation, fetch_query
from datetime import datetime

class ExpenseTracker:
    def __init__(self, user_id, language='English', currency='USD'):
        self.user_id = user_id
        self.language = language
        self.currency = currency

    def get_salary(self, month, year):
        query = "SELECT amount FROM salary WHERE user_id = %s AND month = %s AND year = %s"
        params = (self.user_id, month, year)
        result = execute_db_operation(query, params, fetch=True)
        if result:
            return result[0]['amount']
        else:
            return None

    def update_salary(self, amount, month, year):
        query = "INSERT INTO salary (user_id, amount, month, year) VALUES (%s, %s, %s, %s) ON CONFLICT (user_id, month, year) DO UPDATE SET amount = EXCLUDED.amount RETURNING amount"
        params = (self.user_id, amount, month, year)
        result = execute_db_operation(query, params, fetch=True)
        return result[0]['amount'] if result else None

    def get_categories(self):
        result = execute_db_operation(
            "SELECT name FROM categories WHERE user_id = %s OR user_id IS NULL ORDER BY name",
            (self.user_id,),
            fetch=True
        )
        return [category['name'] for category in result]

    def add_category(self, name):
        check_query = "SELECT COUNT(*) as count FROM categories WHERE (user_id = %s OR user_id IS NULL) AND name = %s"
        result = execute_db_operation(check_query, (self.user_id, name), fetch=True)
        if result[0]['count'] > 0:
            return False, f"Category '{name}' already exists."

        insert_query = "INSERT INTO categories (user_id, name) VALUES (%s, %s)"
        execute_db_operation(insert_query, (self.user_id, name))
        return True, f"Category '{name}' added successfully."

    def remove_category(self, name):
        check_query = "SELECT COUNT(*) as count FROM expenses e JOIN categories c ON e.category_id = c.id WHERE c.user_id = %s AND c.name = %s"
        result = execute_db_operation(check_query, (self.user_id, name), fetch=True)
        if result[0]['count'] > 0:
            return False, f"Cannot remove category '{name}'. It has associated expenses."

        delete_query = "DELETE FROM categories WHERE user_id = %s AND name = %s"
        execute_db_operation(delete_query, (self.user_id, name), fetch=False)
        
        check_deleted_query = "SELECT COUNT(*) as count FROM categories WHERE user_id = %s AND name = %s"
        result = execute_db_operation(check_deleted_query, (self.user_id, name), fetch=True)
        if result[0]['count'] == 0:
            return True, f"Category '{name}' removed successfully."
        else:
            return False, f"Failed to remove category '{name}'. It may not exist."

    def add_expense(self, category, amount, description='', expense_date=None):
        if expense_date is None:
            expense_date = datetime.now().date()
        elif isinstance(expense_date, str):
            try:
                expense_date = datetime.strptime(expense_date, '%Y-%m-%d').date()
            except ValueError:
                return False, "Invalid date format. Please use YYYY-MM-DD."
        elif isinstance(expense_date, datetime):
            expense_date = expense_date.date()

        query = '''
        INSERT INTO expenses (user_id, category_id, amount, description, date, created_at)
        VALUES (%s, (SELECT id FROM categories WHERE (user_id = %s OR user_id IS NULL) AND name = %s LIMIT 1), %s, %s, %s, CURRENT_TIMESTAMP)
        '''
        params = (self.user_id, self.user_id, category, amount, description, expense_date)
        
        try:
            execute_db_operation(query, params)
            return True, "Expense added successfully."
        except Exception as e:
            return False, f"Failed to add expense: {str(e)}"

    def get_expenses(self, month=None, year=None):
        query = """
        SELECT e.id, c.name AS category, e.amount, e.description, e.date, e.created_at
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        WHERE e.user_id = %s
        """
        params = [self.user_id]
        if month and year:
            query += " AND EXTRACT(MONTH FROM e.date) = %s AND EXTRACT(YEAR FROM e.date) = %s"
            params.extend([month, year])
        query += " ORDER BY e.created_at DESC"
        result = fetch_query(query, params)
        return pd.DataFrame(result, columns=['id', 'category', 'amount', 'description', 'date', 'created_at'])

    def remove_expense(self, expense_id):
        query = "DELETE FROM expenses WHERE id = %s AND user_id = %s"
        params = (expense_id, self.user_id)
        execute_db_operation(query, params, fetch=False)
        
        check_query = "SELECT COUNT(*) as count FROM expenses WHERE id = %s AND user_id = %s"
        result = execute_db_operation(check_query, params, fetch=True)
        if result[0]['count'] == 0:
            return True, "Expense removed successfully."
        else:
            return False, "Failed to remove expense. It may not exist or you don't have permission to remove it."

    def get_currency_symbol(self):
        return '₺' if self.currency == 'TRY' else '$'
