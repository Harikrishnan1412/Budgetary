import datetime
from django.shortcuts import render
from django.urls import reverse

from userincome.models import Source, UserIncome
from expenses.models import Category, Expense
from .models import UserPreference
import os
import json
from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator



# Create your views here.
def userinfo(request):
    exists = UserPreference.objects.filter(user=request.user).exists()
    user_perferences = None
    currency_data = []
    file_path = os.path.join(settings.BASE_DIR, 'currencies.json')
        # # Used for Debugging
        # import pdb
        # pdb.set_trace()
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        for k,v in data.items():
            currency_data.append({'name':k, 'value':v})

    if exists:
        user_perferences = UserPreference.objects.get(user=request.user)
    if request.method == 'GET':
        return render(request, 'userperference/index.html',{'currencies':currency_data, 'user_perferences': user_perferences})
    else:
        currency = request.POST['currency']
        if exists:
            user_perferences.currency=currency
            user_perferences.save()
        else:
            UserPreference.objects.create(user=request.user, currency=currency)
        messages.success(request, 'Changes Saved')
        return render(request, 'userperference/index.html',{'currencies':currency_data, 'user_perferences': user_perferences})


def amount_sum(expenses):
    sum = 0
    for i in expenses:
        sum = sum+i.amount
    return sum

def account_detail(request):
    todays_date = datetime.date.today()
    one_week = todays_date - datetime.timedelta(days=7)
    one_month = todays_date - datetime.timedelta(days=30)
    six_months_ago = todays_date - datetime.timedelta(days=30*6)
    one_year = todays_date - datetime.timedelta(days=30*12)
    expenses_week = Expense.objects.filter(owner = request.user, 
                                      date__gte =  one_week, date__lte = todays_date)
    expenses_month = Expense.objects.filter(owner = request.user, 
                                      date__gte = one_month, date__lte = todays_date)
    expenses_six_month = Expense.objects.filter(owner = request.user, 
                                      date__gte = six_months_ago, date__lte = todays_date)
    expenses_year = Expense.objects.filter(owner = request.user, 
                                      date__gte = one_year, date__lte = todays_date)
    income_week = UserIncome.objects.filter(owner = request.user, 
                                      date__gte =  one_week, date__lte = todays_date)
    income_month = UserIncome.objects.filter(owner = request.user, 
                                      date__gte =  one_month, date__lte = todays_date)
    income_six_month = UserIncome.objects.filter(owner = request.user, 
                                      date__gte =  six_months_ago, date__lte = todays_date)
    income_year = UserIncome.objects.filter(owner = request.user, 
                                      date__gte =  one_year, date__lte = todays_date)
    month_sum = 0
    # Expenses table data
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner = request.user)
    #Pagination process
    paginator_expense = Paginator(expenses, 4)
    page_number_expense = request.GET.get('page')
    page_obj_expense = Paginator.get_page(paginator_expense, page_number_expense)
    currency = UserPreference.objects.get(user=request.user).currency
    # End of table data

    # Income table data
    sources = Source.objects.all()
    incomes = UserIncome.objects.filter(owner = request.user)
    #Pagination process
    paginator_income = Paginator(incomes, 4)
    page_number_income = request.GET.get('page')
    page_obj_income = Paginator.get_page(paginator_income, page_number_expense)
    # End of Income


    context = {
        'expenses_week': amount_sum(expenses_week),
        'expenses_month': amount_sum(expenses_month),
        'expenses_six_month':amount_sum(expenses_six_month),
        'expenses_year':amount_sum(expenses_year),
        'income_week': amount_sum(income_week),
        'income_month': amount_sum(income_month),
        'income_six_month': amount_sum(income_six_month),
        'income_year': amount_sum(income_year),
        'expenses': expenses,
        'incomes':incomes,
        'page_obj_expense':page_obj_expense,
        'page_obj_income':page_obj_income,
        'currency':currency

    }
    return render(request, 'userperference/useraccount.html',context)



