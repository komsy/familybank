from django.urls import path
from . import views



urlpatterns = [
    path('', views.index, name='expenses/index.html'),
    # Create new expenses
    path('add-expense/', views.add_expense, name='add-expenses')
]