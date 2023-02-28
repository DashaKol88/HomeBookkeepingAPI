import json

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from .models import Account, Transaction


# Create your views here.
def index(request):
    return HttpResponse("Hello, it's my Bookkeeping!")


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


def user_register(request):
    pass


@login_required(login_url='/auth_error')
def user_account(request):
    account_data = Account.objects.filter(account_owner=request.user)
    account_data = list(account_data.values('account_owner__username', 'account_number', 'account_balance'))
    return JsonResponse({"Account": account_data})


# Transactions

@login_required(login_url='/auth_error')
def transaction_latest(request):
    account_data = get_object_or_404(Account, account_owner=request.user)
    transactions = Transaction.objects.filter(transaction_account=account_data).order_by('-transaction_date')[:10]
    transactions = list(
        transactions.values('transaction_date', 'transaction_type', 'transaction_category__category_name',
                            'transaction_sum',
                            'transaction_comment'))
    return JsonResponse({"transactions": transactions})
