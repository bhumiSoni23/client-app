from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Sum
from django.db.models.functions import TruncMonth
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Expense
from .forms import ExpenseForm
import csv
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from django.shortcuts import redirect


# Register view
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login_view')
    else:
        form = UserCreationForm()
    return render(request, 'tracker/register.html', {'form': form})

# Login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('list_expenses')
    else:
        form = AuthenticationForm()
    return render(request, 'tracker/login.html', {'form': form})

# Logout view
def logout_view(request):
    logout(request)
    return redirect('login_view')

# List expenses view
@login_required
def list_expenses(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')

    query = request.GET.get('q')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if query:
        expenses = expenses.filter(Q(title__icontains=query) | Q(category__icontains=query))

    if start_date:
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        expenses = expenses.filter(date__lte=end_date)

    total_expenses = expenses.count()
    total_amount = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    return render(request, 'tracker/list_expenses.html', {
        'expenses': expenses,
        'total_expenses': total_expenses,
        'total_amount': total_amount,
    })

# Add expense view
@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('list_expenses')
    else:
        form = ExpenseForm()

    return render(request, 'tracker/add_expense.html', {'form': form})

# Update expense view
class UpdateExpenseView(UpdateView):
    model = Expense
    fields = ['title', 'amount', 'category', 'date', 'description']
    template_name = 'tracker/edit_expense.html'
    success_url = reverse_lazy('list_expenses')

# Delete expense view
class DeleteExpenseView(DeleteView):
    model = Expense
    template_name = 'tracker/delete_expense.html'
    success_url = reverse_lazy('list_expenses')

# Dashboard view
@login_required
def dashboard(request):
    expenses = Expense.objects.filter(user=request.user)

    # Optional filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    category = request.GET.get('category')

    if start_date:
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        expenses = expenses.filter(date__lte=end_date)
    if category and category != 'All':
        expenses = expenses.filter(category=category)

    # Monthly aggregation
    monthly_data = expenses.annotate(month=TruncMonth('date')) \
        .values('month') \
        .annotate(total=Sum('amount')) \
        .order_by('month')

    months = [entry['month'].strftime('%B %Y') for entry in monthly_data]
    totals = [float(entry['total']) for entry in monthly_data]

    # Create zipped_data for template
    zipped_data = zip(months, totals)

    # Get all unique categories for the dropdown
    all_categories = Expense.objects.filter(user=request.user).values_list('category', flat=True).distinct()

    return render(request, 'tracker/dashboard.html', {
        'zipped_data': zipped_data,
        'start_date': start_date,
        'end_date': end_date,
        'selected_category': category,
        'all_categories': all_categories,
    })

# Export CSV view
@login_required
def export_csv(request):
    expenses = Expense.objects.filter(user=request.user)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=expenses.csv'

    writer = csv.writer(response)
    writer.writerow(['Title', 'Amount', 'Category', 'Date', 'Description'])

    for expense in expenses:
        writer.writerow([expense.title, expense.amount, expense.category, expense.date, expense.description])

    return response

# Submit expense via API (for JSON requests)
@csrf_exempt  # For testing purposes, remove this in production for security
def submit_expense(request):
    if request.method == 'POST':
        try:
            # Parsing the JSON body from the request
            data = json.loads(request.body)

            title = data.get('title')
            amount = data.get('amount')

            # You can add validation here if necessary
            if not title or not amount:
                return JsonResponse({'error': 'Title and Amount are required'}, status=400)

            # Create the new expense record
            Expense.objects.create(
                user=request.user,  # Assuming the user is logged in
                title=title,
                amount=amount
            )

            # Respond with success
            return JsonResponse({'success': 'Expense submitted successfully!'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
def logout_view(request):
    logout(request)  
    return redirect('login_view')  

