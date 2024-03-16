from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

app_name = 'userincome'
urlpatterns = [
    path('income_list', views.index, name="income_list"),
    path('add-income',views.add_income, name='add-income'),
    path('edit-income/<int:id>', views.income_edit, name='income-edit'),
    path('income-delete/<int:id>', views.income_delete, name='income-delete'),
    path('search-income', csrf_exempt(views.search_income), name='search-income'),
    path('income_summary_sources', views.income_summary_sources, name='income_summary_sources'),
    path('export_csv', views.export_csv, name='export_csv'),
    path('export_xls', views.export_xls, name='export_xls'),
     path('view_stats',views.view_stats, name='view_stats'),
]
