import json

from django.contrib.auth import authenticate, login
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views.decorators.http import require_http_methods


def index(request):
    return HttpResponse("Hello, it's my Bookkeeping!")


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
