from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('auth_error', views.auth_error, name='auth_error'),
    path('api/user/login', views.user_login, name='user_login'),
    path('api/user/account', views.user_account, name='user_account'),
    path('api/transaction/latest', views.transaction_latest, name='transaction_latest'),
    path('api/transaction/filter', views.transaction_filter, name='transaction_filter'),
    path('api/transaction/add', views.transaction_add, name='transaction_add'),
    path('api/transaction/<int:transaction_id>/delete', views.transaction_delete, name='transaction_delete'),

]
