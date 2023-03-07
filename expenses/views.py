from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Expense, Category
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from userpreferences.models import UserPreferences


def search_expenses(request):
    # transform data to py dictionary
    search_str = json.loads(request.body).get('searchText','')  # add optional blank to avoid the search from crushing

    expenses = Expense.objects.filter(amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(date__istartswith=search_str,owner=request.user) | Expense.objects.filter(description__icontains=search_str,owner=request.user) | Expense.objects.filter(category__icontains=search_str,owner=request.user)

    data = expenses.values()
    return JsonResponse(list(data), safe=False)

# protect the home/'' route need to login
@login_required(login_url='/authentication/login')
# Create your views here.
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 2)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator,page_number)
    # change currency upon user input
    currency = UserPreferences.objects.get(user=request.user).currency
    
    context = {
        'currency':currency,
        'expenses':expenses,
        'page_obj':page_obj,
    }
    return render(request,'expenses/index.html',context)

def add_expense(request):
    categories = Category.objects.all()
    context = {
        'categories':categories,
        'values': request.POST  # return same values on error
    }
    if request.method == 'GET':
        return render(request,'expenses/add_expense.html',context)

    if request.method == 'POST':
        amount = request.POST['amount']
        if not amount:
            messages.error(request,'Amount is required')
            return render(request,'expenses/add_expense.html',context)

        date = request.POST['expense_date']
        category = request.POST['category']
        description = request.POST['description']

        if not description:
            messages.error(request,'Description is required')
            return render(request,'expenses/add_expense.html',context)

        Expense.objects.create(owner=request.user,amount=amount,date=date,category=category,description=description)
        messages.success(request, 'Expense saved successfully')

        return redirect('expenses')

# edit expense
def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories,
    }
    if request.method == 'GET':
        return render(request, 'expenses/edit-expense.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']
        if not amount:
            messages.error(request,'Amount is required')
            return render(request,'expenses/edit-expense.html',context)

        date = request.POST['expense_date']
        category = request.POST['category']
        description = request.POST['description']

        if not description:
            messages.error(request,'Description is required')
            return render(request,'expenses/edit-expense.html',context)

        expense.owner=request.user
        expense.amount=amount
        expense.date=date
        expense.category=category
        expense.description=description
        expense.save()
        
        messages.success(request, 'Expense updated successfully')

        return redirect('expenses')
    else:
        messages.info(request, 'Handling post form')

# delete expense
def expense_delete(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()

    messages.success(request, 'Expense deleted successfully')
    return redirect('expenses')