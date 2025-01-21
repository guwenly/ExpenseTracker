import plotly.graph_objects as go
import plotly.express as px

translations = {
    'English': {
        'Expense Distribution by Category': 'Expense Distribution by Category',
        'Expense Comparison Across Months and Years': 'Expense Comparison Across Months and Years',
        'Category-wise Expense Comparison Across Months and Years': 'Category-wise Expense Comparison Across Months and Years',
        'Total Expenses': 'Total Expenses',
        'Month': 'Month',
        'Year': 'Year',
        'Expenses': 'Expenses',
        'Category': 'Category'
    },
    'Turkish': {
        'Expense Distribution by Category': 'Kategoriye Göre Gider Dağılımı',
        'Expense Comparison Across Months and Years': 'Aylar ve Yıllar Arası Gider Karşılaştırması',
        'Category-wise Expense Comparison Across Months and Years': 'Aylar ve Yıllar Arası Kategoriye Göre Gider Karşılaştırması',
        'Total Expenses': 'Toplam Giderler',
        'Month': 'Ay',
        'Year': 'Yıl',
        'Expenses': 'Giderler',
        'Category': 'Kategori'
    }
}

def create_expense_pie_chart(expenses_df, currency_symbol='$', lang='English'):
    grouped_expenses = expenses_df.groupby('category')['amount'].sum().reset_index()
    
    fig = go.Figure(data=[go.Pie(
        labels=grouped_expenses['category'],
        values=grouped_expenses['amount'],
        hole=0.3,
        textinfo='label+percent',
        insidetextorientation='radial'
    )])
    
    fig.update_layout(
        title=translations[lang]['Expense Distribution by Category'],
        height=500,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    
    fig.update_traces(texttemplate='%{label}<br>' + currency_symbol + '%{value:.2f}')
    
    return fig

def create_expense_comparison_chart(comparison_df, currency_symbol='$', lang='English'):
    fig = px.bar(comparison_df, x='month', y='total_expenses', color='year', barmode='group',
                 labels={'total_expenses': f"{translations[lang]['Total Expenses']} ({currency_symbol})", 'month': translations[lang]['Month'], 'year': translations[lang]['Year']},
                 title=translations[lang]['Expense Comparison Across Months and Years'])
    
    fig.update_layout(
        xaxis_title=translations[lang]['Month'],
        yaxis_title=f"{translations[lang]['Total Expenses']} ({currency_symbol})",
        legend_title=translations[lang]['Year'],
        height=500,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    
    return fig

def create_category_comparison_chart(comparison_df, currency_symbol='$', lang='English'):
    fig = px.bar(comparison_df, x='month', y='amount', color='category', barmode='stack',
                 facet_col='year', facet_col_wrap=2,
                 labels={'amount': f"{translations[lang]['Expenses']} ({currency_symbol})", 'month': translations[lang]['Month'], 'category': translations[lang]['Category']},
                 title=translations[lang]['Category-wise Expense Comparison Across Months and Years'])
    
    fig.update_layout(
        xaxis_title=translations[lang]['Month'],
        yaxis_title=f"{translations[lang]['Expenses']} ({currency_symbol})",
        legend_title=translations[lang]['Category'],
        height=600,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    
    # Update facet titles to show only the year
    for annotation in fig.layout.annotations:
        annotation.text = annotation.text.split("=")[-1]
    
    return fig
