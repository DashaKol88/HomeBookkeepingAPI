import json
from datetime import datetime
from decimal import Decimal

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum, FloatField

from django.http import HttpResponse, JsonResponse, HttpRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from .models import Account, Transaction, TransactionCategory, PlanningTransaction


# Create your views here.
@require_http_methods(["GET"])
def index(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Hello, it's my Bookkeeping!")


@require_http_methods(["GET"])
def auth_error(request: HttpRequest) -> JsonResponse:
    """
    Return a JSON response with 401 status code indicating that the user is not authenticated.
    :param request: The HTTP request object.
    :type request: HttpRequest
    :return: The JSON response containing the authentication error message.
    :rtype: JsonResponse
    """
    return JsonResponse(status=401, data={"Authenticated": "false"})


# users
@require_http_methods(["POST"])
def user_login(request: HttpRequest) -> JsonResponse:
    """
    Logs in the user with the provided credentials.
    :param request: The HTTP request object.
    :type request: HttpRequest
    :return: A JsonResponse object containing authentication status.
    :rtype: JsonResponse
    """
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


@login_required(login_url='/auth_error')
def user_logout(request: HttpRequest) -> JsonResponse:
    """
    Logs out the authenticated user and returns a JSON response with a status of 200 and data indicating successful
    logout.
    :param request: the HTTP request object
    :type request: HttpRequest
    :return: JSON response indicating successful logout
    :rtype: JsonResponse
    """
    logout(request)
    return JsonResponse(status=200, data={"Logout": "true"})


@require_http_methods(["POST"])
def user_register(request: HttpRequest) -> JsonResponse:
    """
    Registers a new user and logs them in.
    :param request: The HTTP request object.
    :type request: HttpRequest
    :return: A JSON response indicating success or failure of the registration attempt.
    :rtype: JsonResponse
    """
    try:
        data = json.loads(request.body)
        username = data['username']
        password = data['password']
        email = data['email']
        if username and password and email:
            new_user = User.objects.create_user(username=username, email=email, password=password)
            login(request, new_user)
            new_account = Account(account_owner=new_user, account_number=0,
                                  account_balance=Decimal(0))
            new_account.save()
            return JsonResponse(status=200, data={"register": new_user.id})
        else:
            return JsonResponse(status=400, data={"error": "Not all required fields are filled"})
    except:
        return JsonResponse(status=400, data={"error": "Bad request"})


@login_required(login_url='/auth_error')
@require_http_methods(["GET"])
def user_account(request: HttpRequest) -> JsonResponse:
    """
    Returns account data for the authenticated user.
    :param request: The HTTP request object.
    :type request: HttpRequest
    :return: A JSON response with account data.
    :rtype: JsonResponse
    """
    account_data = Account.objects.filter(account_owner=request.user)
    account_data = list(account_data.values('account_owner__username', 'account_number', 'account_balance'))
    return JsonResponse(status=200, data={"Account": account_data})


# Transactions

@login_required(login_url='/auth_error')
@require_http_methods(["GET"])
def transaction_latest(request: HttpRequest) -> JsonResponse:
    """
    Returns the latest transactions for the authenticated user.
    :param request: The HTTP request object.
    :type request: HttpRequest
    :return: JSON object containing the latest transactions.
    :rtype: JsonResponse
    """
    account_data = get_object_or_404(Account, account_owner=request.user)
    transactions = Transaction.objects.filter(transaction_account=account_data).order_by('-transaction_date')
    transactions = list(
        transactions.values('id', 'transaction_date', 'transaction_type', 'transaction_category__category_name',
                            'transaction_sum',
                            'transaction_comment'))
    return JsonResponse(status=200, data={"transactions": transactions})


@login_required(login_url='/auth_error')
@require_http_methods(["GET"])
def transaction_filter(request: HttpRequest) -> JsonResponse:
    """
    View function for filtering transactions based on various parameters.
    :param request: The HTTP request object.
    :type request: HttpRequest
    :return: A JSON response containing a list of filtered transactions.
    :rtype: JsonResponse
    """
    account_data = get_object_or_404(Account, account_owner=request.user)
    transactions = Transaction.objects.filter(transaction_account=account_data).order_by('-transaction_date')

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

    return JsonResponse(status=200, data={"transactions": transactions})


@login_required(login_url='/auth_error')
@require_http_methods(["GET"])
def transaction_statistic(request: HttpRequest) -> JsonResponse:
    """
    Function for statistics on transactions for the selected period. Gives the total amount of income and expenses
    and the amount for each category of transactions.
    :param request: The HTTP request object.
    :type request: HttpRequest
    :return: JsonResponse object with transaction statistics.
    :rtype: JsonResponse
    """
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

    transaction_inc_sum = transactions.filter(transaction_type=1).aggregate(
        overall_income=Sum('transaction_sum', output_field=FloatField()))
    transaction_exp_sum = transactions.filter(transaction_type=0).aggregate(
        overall_expense=Sum('transaction_sum', output_field=FloatField()))

    category_list = list(transactions.values('transaction_category__category_name'))
    category_name_list = [
        *set(category_list[i]['transaction_category__category_name'] for i in range(len(category_list)))]
    statistic_data = [transaction_inc_sum, transaction_exp_sum]
    for c in category_name_list:
        statistic_data.append({c: transactions.filter(transaction_category__category_name=c).aggregate(
            Sum('transaction_sum', output_field=FloatField()))["transaction_sum__sum"]})

    return JsonResponse(status=200, data={"statistic_data": statistic_data})


@login_required(login_url='/auth_error')
@require_http_methods(["POST"])
def transaction_add(request: HttpRequest) -> JsonResponse:
    """Add a new transaction to the account of the logged-in user.
    :param request: The HTTP request object.
    :type request: HttpRequest
    :return: JsonResponse object with the ID of the added transaction.
    A JsonResponse with an error message if the request fails.
    :rtype: JsonResponse
    """
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

    return JsonResponse(status=200, data={"transaction": transaction.id})


@login_required(login_url='/auth_error')
@require_http_methods(["POST"])
def transaction_delete(request: HttpRequest, transaction_id: int) -> JsonResponse:
    """
    Delete a specific transaction record and update account balance
    :param request: The HTTP request object.
    :type request: HttpRequest
    :param transaction_id: ID of the transaction to be deleted
    :type transaction_id: int
    :return: JsonResponse object with status and deleted transaction ID
    :rtype: JsonResponse
    """
    account_data = get_object_or_404(Account, account_owner=request.user)
    transaction = get_object_or_404(Transaction, pk=transaction_id, transaction_account=account_data)
    if transaction.transaction_type == 1:
        account_data.account_balance -= transaction.transaction_sum
    else:
        account_data.account_balance += transaction.transaction_sum
    account_data.save()
    transaction_id = transaction.id
    transaction.delete()
    return JsonResponse(status=200, data={"transaction": transaction_id})


# Categories
@require_http_methods(["GET"])
def categories(request: HttpRequest) -> JsonResponse:
    """
    The function returns a list of transaction categories with their types.
    :param request: The HTTP request object.
    :type request: HttpRequest
    :return: JsonResponse object with data on transaction categories
    :rtype: JsonResponse
    """
    category_list = list(TransactionCategory.objects.all().values('category_type', 'category_name'))
    return JsonResponse(status=200, data={'data': category_list})


# Planning
@login_required(login_url='/auth_error')
@require_http_methods(["GET"])
def planned_transactions(request: HttpRequest) -> JsonResponse:
    """
    Returns a list of planned transactions for the current user.
    :param request: The HTTP request object.
    :type request: HttpRequest
    :return: A JSON response containing a list of planned transactions.
    :rtype: JsonResponse
    """
    account_data = get_object_or_404(Account, account_owner=request.user)
    transactions = PlanningTransaction.objects.filter(transaction_account_plan=account_data).order_by(
        '-transaction_date_plan')
    transactions = list(
        transactions.values('id', 'transaction_date_plan', 'transaction_type_plan',
                            'transaction_category_plan__category_name',
                            'transaction_sum_plan',
                            'transaction_comment_plan'))

    return JsonResponse(status=200, data={"transactions": transactions})


@login_required(login_url='/auth_error')
@require_http_methods(["POST"])
def planned_transaction_add(request: HttpRequest) -> JsonResponse:
    """
    Adds a new planned transaction to the specified account.
    :param request: The HTTP request object.
    :type request: HttpRequest
    :return: A JsonResponse containing the ID of the created transaction if the request is successful.
    A JsonResponse with an error message if the request fails.
    :rtype: JsonResponse
    """
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

    transaction = PlanningTransaction(transaction_account_plan=account_data, transaction_type_plan=transaction_type,
                                      transaction_category_plan=transaction_category,
                                      transaction_date_plan=transaction_date,
                                      transaction_sum_plan=transaction_sum,
                                      transaction_comment_plan=transaction_comment)

    transaction.save()

    return JsonResponse(status=200, data={"transaction": transaction.id})


@login_required(login_url='/auth_error')
@require_http_methods(["POST"])
def planned_transaction_delete(request: HttpRequest, transaction_id: int) -> JsonResponse:
    """
    This function deletes a planned transaction for the authenticated user.
    :param request: The HTTP request object.
    :type request: HttpRequest
    :param transaction_id: The ID of the transaction to delete.
    :type transaction_id: int
    :return: A JSON response indicating success or failure of the operation.
    :rtype: JsonResponse
    """
    account_data = get_object_or_404(Account, account_owner=request.user)
    transaction = get_object_or_404(PlanningTransaction, pk=transaction_id, transaction_account_plan=account_data)
    transaction_id = transaction.id
    transaction.delete()
    return JsonResponse(status=200, data={"transaction": transaction_id})


@login_required(login_url='/auth_error')
@require_http_methods(["GET"])
def planned_transaction_statistic(request: HttpRequest) -> JsonResponse:
    """
    Function for statistics on transactions for the selected period. Gives the total amount of income and expenses.
    :param request: The HTTP request object.
    :type request: HttpRequest
    :return: JsonResponse object with transaction statistics.
    :rtype: JsonResponse
    """
    account_data = get_object_or_404(Account, account_owner=request.user)
    transactions = PlanningTransaction.objects.filter(transaction_account_plan=account_data)

    transaction_start_date = request.GET.get("transaction_start_date")
    transaction_end_date = request.GET.get("transaction_end_date")

    if transaction_start_date and transaction_end_date:
        transaction_start_date = datetime.strptime(transaction_start_date, '%Y-%m-%d')
        transaction_end_date = datetime.strptime(transaction_end_date, '%Y-%m-%d')
        transactions = transactions.filter(transaction_date_plan__range=[transaction_start_date, transaction_end_date])
    else:
        return JsonResponse(status=400, data={"error": "Bad request"})

    transaction_inc_sum = transactions.filter(transaction_type_plan=1).aggregate(
        planned_income=Sum('transaction_sum_plan', output_field=FloatField()))
    transaction_exp_sum = transactions.filter(transaction_type_plan=0).aggregate(
        planned_expense=Sum('transaction_sum_plan', output_field=FloatField()))
    statistic_data = [transaction_inc_sum, transaction_exp_sum]
    return JsonResponse(status=200, data={"statistic_data": statistic_data})
