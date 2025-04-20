from django.urls import path
from . import views
from .views import UpdateExpenseView, DeleteExpenseView

urlpatterns = [
    
    path('add/', views.add_expense, name='add_expense'),
    path('edit/<int:pk>/', UpdateExpenseView.as_view(), name='update_expense'),
    path('delete/<int:pk>/', DeleteExpenseView.as_view(), name='delete_expense'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register_view, name='register_view'),
    path('', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
    path('export-csv/', views.export_csv, name='export_csv'),
    path('list/', views.list_expenses, name='list_expenses'),
    path("submit-expense/", views.submit_expense, name="submit_expense"),
    path('logout/', views.logout_view, name='logout_view'),

]