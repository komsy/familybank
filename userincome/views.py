from django.contrib.auth.decorators import login_required
from userpreferences.models import UserPreferences
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from .models import UserIncome, Source
from django.http import JsonResponse
from django.contrib import messages
import datetime
import json


def search_income(request):
    # transform data to py dictionary
    search_str = json.loads(request.body).get('searchText','')  # add optional blank to avoid the search from crushing

    income = UserIncome.objects.filter(amount__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(date__istartswith=search_str,owner=request.user) | UserIncome.objects.filter(description__icontains=search_str,owner=request.user) | UserIncome.objects.filter(source__icontains=search_str,owner=request.user)

    data = income.values()
    return JsonResponse(list(data), safe=False)

# protect the home/'' route need to login
@login_required(login_url='/authentication/login')
# Create your views here.
def index(request):
    source = Source.objects.all()
    income = UserIncome.objects.filter(owner=request.user)
    paginator = Paginator(income, 2)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator,page_number)
    # change currency upon user input
    currency = UserPreferences.objects.get(user=request.user).currency
    
    context = {
        'currency':currency,
        'income':income,
        'page_obj':page_obj,
    }
    return render(request,'income/index.html',context)

def add_income(request):
    sources = Source.objects.all()
    context = {
        'sources':sources,
        'values': request.POST  # return same values on error
    }
    if request.method == 'GET':
        return render(request,'income/add_income.html',context)

    if request.method == 'POST':
        amount = request.POST['amount']
        if not amount:
            messages.error(request,'Amount is required')
            return render(request,'income/add_income.html',context)

        date = request.POST['income_date']
        source = request.POST['source']
        description = request.POST['description']

        if not description:
            messages.error(request,'Description is required')
            return render(request,'Income/add_income.html',context)

        UserIncome.objects.create(owner=request.user,amount=amount,date=date,source=source,description=description)
        messages.success(request, 'Income saved successfully')

        return redirect('income')

# edit income
def income_edit(request, id):
    income = UserIncome.objects.get(pk=id)
    sources = Source.objects.all()
    context = {
        'income': income,
        'values': income,
        'sources': sources,
    }
    if request.method == 'GET':
        return render(request, 'income/edit-income.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']
        if not amount:
            messages.error(request,'Amount is required')
            return render(request,'income/edit-income.html',context)

        date = request.POST['income_date']
        source = request.POST['source']
        description = request.POST['description']

        if not description:
            messages.error(request,'Description is required')
            return render(request,'income/edit-income.html',context)

        income.owner=request.user
        income.amount=amount
        income.date=date
        income.source=source
        income.description=description
        income.save()
        
        messages.success(request, 'Income updated successfully')

        return redirect('income')
    else:
        messages.info(request, 'Handling post form')

# delete income
def income_delete(request, id):
    income = UserIncome.objects.get(pk=id)
    income.delete()

    messages.success(request, 'Income deleted successfully')
    return redirect('income')


def incomeStats_view(request):
    return render (request, 'income/income_stats.html')

# return incomes summary
def income_source_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date-datetime.timedelta(30*6)
    incomes = UserIncome.objects.filter(owner=request.user, date__gte=six_months_ago, date__lte=todays_date)  
    finalrep = {}  

    def get_source(expense):
        return expense.source

    source_list = list(set(map(get_source, incomes)))

    def get_income_source_amount(source):
        amount = 0
        filtered_by_source = incomes.filter(source=source)

        for item in filtered_by_source:
            amount+= item.amount
        return amount

    for x in incomes:
        for y in source_list:
            finalrep[y] = get_income_source_amount(y)
    return JsonResponse({'income_source_data': finalrep}, safe=False)

