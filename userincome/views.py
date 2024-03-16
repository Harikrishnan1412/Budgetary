import csv
import datetime
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from .models import UserIncome, Source
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import HttpResponse, JsonResponse
from userpreference.models import UserPreference
import xlwt

# Create your views here.
def search_income(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        income = UserIncome.objects.filter(
            amount__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            date__icontains=search_str, owner=request.user)   | UserIncome.objects.filter(
            description__icontains=search_str, owner=request.user) | UserIncome.objects.filter(
            source__icontains=search_str, owner=request.user)
        data = income.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login')
def index(request, *args, **kwargs):
    print("Inside Home")
    sources = Source.objects.all()
    incomes = UserIncome.objects.filter(owner = request.user)
    #Pagination process
    paginator = Paginator(incomes, 2)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    context = {
        'income': incomes,
        'page_obj':page_obj,
        'currency':currency
    }
    #End of pagination process
    return render(request, 'userincome/index.html', context)
# Income CSV
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Incomes '+ str(request.user)+'\ '+ str(datetime.datetime.now())+'.csv'
    writer = csv.writer(response)
    writer.writerow(['Amount', 'Description', 'Source', 'Date'])
    incomes = UserIncome.objects.filter(owner=request.user).order_by('-date')
    for income in incomes:
        writer.writerow([income.amount, income.description, income.source, income.date])
    return response
# End of CSV

# Income of XLS
def export_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Income '+ str(request.user)+'\ '+ str(datetime.datetime.now())+'.xls'

    # Work book
    wb = xlwt.Workbook(encoding='utf-8')
    # Work sheet
    ws = wb.add_sheet('Income')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    #Adding Columns
    columns = ['Amount', 'Description', 'Source', 'Date']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    font_style = xlwt.XFStyle()

    # Getting Row
    rows = UserIncome.objects.filter(owner=request.user).values_list(
        'amount', 'description', 'source', 'date'
    ).order_by('-date')
    for row in rows:
        row_num +=1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)
    wb.save(response)
    return response
# End of Income_XLS


def add_income(request, *args, **kwargs):
    Sources = Source.objects.all()
    context = {
        'sources':Sources,
        'values':request.POST
    }
    if request.method == 'GET':
        return render(request, 'userincome/add_income.html', context)  
    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']
        if not amount:
            messages.error(request, 'Amount is Required')
            return render(request, 'userincome/add_income.html', context) 
        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'userincome/add_income.html', context) 
        if not date:
            messages.error(request, 'Date is required')
            return render(request, 'userincome/add_income.html', context) 
        if not source:
            messages.error(request, 'source is required')
            return render(request, 'userincome/add_income.html', context) 
        UserIncome.objects.create(owner=request.user, amount=amount, date=date, source=source ,description=description)
        messages.success(request, 'Expense Added Successfully')
        return redirect('userincome:income_list')
    
def income_edit(request, id):
    income = UserIncome.objects.get(pk=id)
    sources = Source.objects.all()
    context = {
        'income':income,
        'sources':sources
    }
    if request.method == 'GET':
        return render(request, 'userincome/edit_income.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']
        if not amount:
            messages.error(request, 'Amount is Required')
            return render(request, 'userincome/edit_income.html', context) 
        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'userincome/edit_income.html', context) 
        if not date:
            messages.error(request, 'Date is required')
            return render(request, 'userincome/edit_income.html', context) 
        if not source:
            messages.error(request, 'Source is required')
            return render(request, 'userincome/edit_income.html', context) 
        income.amount = amount
        income.description = description
        income.date=date
        income.source = source
        income.save()
        messages.success(request, 'Income Added Successfully')
        return redirect('userincome:income_list')
        
def income_delete(request, id):
    income = UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request, 'Income removed')
    return redirect('income')

def view_stats(request):
    print("INside view stats")
    return render(request, 'userincome/incomestats.html')

def income_summary_sources(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30*6)
    # Filter objects of last 6 months
    incomes = UserIncome.objects.filter(owner = request.user, 
                                      date__gte = six_months_ago, date__lte = todays_date)
    finalrep = {}

    def get_source(income):
        return income.source
    # Calling get_source method to find only avaliable source that user done expense
    source_list = list(set(map(get_source, incomes)))

    def get_income_source_amount(source):
        amount = 0
        filtered_by_source = incomes.filter(source=source)
        for item in filtered_by_source:
            amount += item.amount
        return amount    
    # Calling every expense inside user
    # And expense made under every source
    for x in incomes:
        for y in source_list:
            print(y)
            finalrep[y] = get_income_source_amount(y)

    return JsonResponse({'income_source_data':finalrep},safe=False)
