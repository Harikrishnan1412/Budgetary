from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from .models import Expense, Category
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse, HttpResponse
import csv
import xlwt
from userpreference.models import UserPreference
import datetime
from django.template.loader import render_to_string
# from weasyprint import HTML
import tempfile
from django.db.models import Sum

# Search function get value
# Filter using "istartswith" or "icontain"
# return JsonResponse
def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expense = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__icontains=search_str, owner=request.user)   | Expense.objects.filter(
            description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user)
        data = expense.values()
        return JsonResponse(list(data), safe=False)

# Create your views here.
#@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/authentication/login')
def index(request, *args, **kwargs):
    print("Inside Home")
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner = request.user)
    #Pagination process
    paginator = Paginator(expenses, 4)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    context = {
        'expenses': expenses,
        'page_obj':page_obj,
        'currency':currency
    }
    #End of pagination process
    return render(request, 'expenses/index.html', context)

def add_expense(request, *args, **kwargs):
    categories = Category.objects.all()
    context = {
        'categories':categories,
        'values':request.POST
    }
    if request.method == 'GET':
        return render(request, 'expenses/add_expenses.html', context)  
    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']
        if not amount:
            messages.error(request, 'Amount is Required')
            return render(request, 'expenses/add_expenses.html', context) 
        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'expenses/add_expenses.html', context) 
        if not date:
            messages.error(request, 'Date is required')
            return render(request, 'expenses/add_expenses.html', context) 
        if not category:
            messages.error(request, 'Category is required')
            return render(request, 'expenses/add_expenses.html', context) 
        Expense.objects.create(owner=request.user, amount=amount, date=date, category=category,description=description)
        messages.success(request, 'Expense Added Successfully')
        return redirect('expenses')
    

def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = {
        'expense':expense,
        'categories':categories
    }
    if request.method == 'GET':
        return render(request, 'expenses/edit-expense.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']
        if not amount:
            messages.error(request, 'Amount is Required')
            return render(request, 'expenses/edit-expense.html', context) 
        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'expenses/edit-expense.html', context) 
        if not date:
            messages.error(request, 'Date is required')
            return render(request, 'expenses/edit-expense.html', context) 
        if not category:
            messages.error(request, 'Category is required')
            return render(request, 'expenses/edit-expense.html', context) 
        expense.amount = amount
        expense.description = description
        expense.date=date
        expense.category = category
        expense.save()
        messages.success(request, 'Expense Added Successfully')
        return redirect('expenses')
        
def expense_delete(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense removed')
    return redirect('expenses')

def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30*6)
    # Filter objects of last 6 months
    expenses = Expense.objects.filter(owner = request.user, 
                                      date__gte = six_months_ago, date__lte = todays_date)
    finalrep = {}

    def get_category(expense):
        return expense.category
    # Calling get_category method to find only avaliable category that user done expense
    category_list = list(set(map(get_category, expenses)))

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)
        for item in filtered_by_category:
            amount += item.amount
        return amount    
    # Calling every expense inside user
    # And expense made under every category
    for x in expenses:
        for y in category_list:
            finalrep[y] = get_expense_category_amount(y)

    return JsonResponse({'expense_category_data':finalrep},safe=False)


def stats_view(request):
    return render(request, 'expenses/stats.html')
    

def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Expenses '+ str(request.user)+'\ '+ str(datetime.datetime.now())+'.csv'
    writer = csv.writer(response)
    writer.writerow(['Amount', 'Description', 'Category', 'Date'])
    expenses = Expense.objects.filter(owner=request.user).order_by('-date')
    for expense in expenses:
        writer.writerow([expense.amount, expense.description, expense.category, expense.date])
    return response

def export_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Expenses '+ str(request.user)+'\ '+ str(datetime.datetime.now())+'.xls'

    # Work book
    wb = xlwt.Workbook(encoding='utf-8')
    # Work sheet
    ws = wb.add_sheet('Expense')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    #Adding Columns
    columns = ['Amount', 'Description', 'Category', 'Date']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    font_style = xlwt.XFStyle()

    # Getting Row
    rows = Expense.objects.filter(owner=request.user).values_list(
        'amount', 'description', 'category', 'date'
    ).order_by('-date')
    for row in rows:
        row_num +=1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)
    wb.save(response)
    return response

# Error in below code in future use doc instead of PDF
# def export_pdf(request):
#     response = HttpResponse(content_type='application/pdf')
#     # Adding 'inline' for open file in browser
#     response['Content-Disposition'] = 'inline; attachment; filename=Expenses '+ str(request.user)+'\ '+ str(datetime.datetime.now())+'.pdf'
#     response['Content-Transfer-Encoding'] = 'binary'
#     # Calling HTML file with context to create pdf
#     html_string = render_to_string('expenses/pdf-output.html', {'expenses':[], 'total':[]})
#     html = HTML(string=html_string)
#     result = html.write_pdf()

#     # this line code preview file before downloading
#     with tempfile.NamedTemporaryFile(delete=True) as output:
#         output.write(result)
#         output.flush()
#         # Passing rb because opening binary file
#         output = open(output.name, 'rb')
#         response.write(output.read())
    
#     return response

