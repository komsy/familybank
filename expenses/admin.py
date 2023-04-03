from django.contrib import admin
from .models import Expense, Category



# Register your models here.
# format to display data in expense tab in the backend
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('owner','category','description','amount','date')
    search_fields = ('category','description','date')

    # items you want to list after search
    list_per_page = 2

admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Category)
