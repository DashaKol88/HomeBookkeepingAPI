import json
from datetime import datetime
from decimal import Decimal

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from .models import Account, Transaction, TransactionCategory, PlanningTransaction


# Create your views here.
@require_http_methods(["GET"])
def index(request):
    return HttpResponse("Hello, it's my Bookkeeping!")


@require_http_methods(["GET"])
def auth_error(request):
    return JsonResponse(status=401, data={"Authenticated": "false"})


# users
@require_http_methods(["POST"])
def user_login(request):
    try:
        data = json.loads(request.body)
        username = data['username']
        password = data['password']
    except:
        return JsonResponse(status=400, data={"error": "Bad request"})
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse(status=200, data={"Authenticated": "true"})
    else:
        return JsonResponse(status=401, data={"Authenticated": "false"})


@require_http_methods(["POST"])
def user_register(request):
    pass


@login_required(login_url='/auth_error')
@require_http_methods(["GET"])
def user_account(request):
    account_data = Account.objects.filter(account_owner=request.user)
    account_data = list(account_data.values('account_owner__username', 'account_number', 'account_balance'))
    return JsonResponse({"Account": account_data})


# Transactions

@login_required(login_url='/auth_error')
@require_http_methods(["GET"])
def transaction_latest(request):
    account_data = get_object_or_404(Account, account_owner=request.user)
    transactions = Transaction.objects.filter(transaction_account=account_data).order_by('-transaction_date')
    transactions = list(
        transactions.values('transaction_date', 'transaction_type', 'transaction_category__category_name',
                            'transaction_sum',
                            'transaction_comment'))
    return JsonResponse({"transactions": transactions})


@login_required(login_url='/auth_error')
@require_http_methods(["GET"])
def transaction_filter(request):
    account_data = get_object_or_404(Account, account_owner=request.user)
    transactions = Transaction.objects.filter(transaction_account=account_data)

    transaction_date = request.GET.get("transaction_date")
    transaction_type = request.GET.get("transaction_type")
    transaction_category = request.GET.get("transaction_category")
    transaction_start_date = request.GET.get("transaction_start_date")
    transaction_end_date = request.GET.get("transaction_end_date")

    if transaction_date:
        transaction_date = datetime.strptime(transaction_date, '%Y-%m-%d')
        transactions = transactions.filter(transaction_date=transaction_date)
    elif transaction_start_date and transaction_end_date:
        transaction_start_date = datetime.strptime(transaction_start_date, '%Y-%m-%d')
        transaction_end_date = datetime.strptime(transaction_end_date, '%Y-%m-%d')
        transactions = transactions.filter(transaction_date__range=[transaction_start_date, transaction_end_date])

    if transaction_type and transaction_type == "Expense":
        transactions = transactions.filter(transaction_type=0)
    elif transaction_type and transaction_type == "Income":
        transactions = transactions.filter(transaction_type=1)

    if transaction_category:
        transactions = transactions.filter(transaction_category__category_name=transaction_category)

    transactions = list(
        transactions.values('transaction_date', 'transaction_type', 'transaction_category__category_name',
                            'transaction_sum', 'transaction_comment'))

    return JsonResponse({"transactions": transactions})


@login_required(login_url='/auth_error')
@require_http_methods(["GET"])
def transaction_statistic(request):
    account_data = get_object_or_404(Account, account_owner=request.user)
    transactions = Transaction.objects.filter(transaction_account=account_data)

    transaction_start_date = request.GET.get("transaction_start_date")
    transaction_end_date = request.GET.get("transaction_end_date")

    if transaction_start_date and transaction_end_date:
        transaction_start_date = datetime.strptime(transaction_start_date, '%Y-%m-%d')
        transaction_end_date = datetime.strptime(transaction_end_date, '%Y-%m-%d')
        transactions = transactions.filter(transaction_date__range=[transaction_start_date, transaction_end_date])
    else:
        return JsonResponse(status=400, data={"error": "Bad request"})

    transaction_inc_sum = transactions.filter(transaction_type=1).aggregate(overall_income=Sum('transaction_sum'))
    transaction_exp_sum = transactions.filter(transaction_type=0).aggregate(overall_expense=Sum('transaction_sum'))

    category_list = list(transactions.values('transaction_category__category_name'))
    category_name_list = [
        *set(category_list[i]['transaction_category__category_name'] for i in range(len(category_list)))]
    statistic_data = [transaction_inc_sum, transaction_exp_sum]
    for c in category_name_list:
        statistic_data.append({c: transactions.filter(transaction_category__category_name=c).aggregate(
            Sum('transaction_sum'))["transaction_sum__sum"]})

    return JsonResponse({"statistic_data": statistic_data})


@login_required(login_url='/auth_error')
@require_http_methods(["POST"])
def transaction_add(request):
    account_data = get_object_or_404(Account, account_owner=request.user)
    try:
        data = json.loads(request.body)
        transaction_type = int(data['transaction_type'])
        transaction_category = TransactionCategory.objects.get(category_name=str(data['transaction_category']))
        transaction_date = datetime.strptime(data['transaction_date'], '%Y-%m-%d')
        transaction_sum = abs(Decimal(data['transaction_sum']))
        transaction_comment = str(data['transaction_comment'])
    except:
        return JsonResponse(status=400, data={"error": "Bad request"})

    transaction = Transaction(transaction_account=account_data, transaction_type=transaction_type,
                              transaction_category=transaction_category, transaction_date=transaction_date,
                              transaction_sum=transaction_sum, transaction_comment=transaction_comment)
    if transaction_type == 1:
        account_data.account_balance += transaction_sum
    elif transaction_type == 0:
        account_data.account_balance -= transaction_sum
    else:
        return JsonResponse(status=400, data={"error": "Bad request"})

    account_data.save()
    transaction.save()

    return JsonResponse({"transaction": transaction.id})


@login_required(login_url='/auth_error')
@require_http_methods(["POST"])
def transaction_delete(request, transaction_id):
    account_data = get_object_or_404(Account, account_owner=request.user)
    transaction = get_object_or_404(Transaction, pk=transaction_id, transaction_account=account_data)
    if transaction.transaction_type == 1:
        account_data.account_balance -= transaction.transaction_sum
    else:
        account_data.account_balance += transaction.transaction_sum
    account_data.save()
    transaction_id = transaction.id
    transaction.delete()
    return JsonResponse({"transaction": transaction_id})


# Categories
@require_http_methods(["GET"])
def categories(request):
    category_list = list(TransactionCategory.objects.all().values('category_type', 'category_name'))
    return JsonResponse({'data': category_list})


# Planning
@login_required(login_url='/auth_error')
@require_http_methods(["GET"])
def planned_transactions(request):
    account_data = get_object_or_404(Account, account_owner=request.user)
    transactions = PlanningTransaction.objects.filter(transaction_account_plan=account_data).order_by('-transaction_date_plan')[:10]
    transactions = list(
        transactions.values('transaction_date_plan', 'transaction_type_plan', 'transaction_category_plan__category_name',
                            'transaction_sum_plan',
                            'transaction_comment_plan'))
    return JsonResponse({"transactions": transactions})

