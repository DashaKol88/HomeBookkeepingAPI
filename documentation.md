### user login
/api/user/login  
method: POST  
```
POST /api/user/login HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json

{"username":"Dasha","password":"testpassword123"}
```


### user logout
api/user/logout
```
GET /api/user/logout HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json
```

### user register
api/user/register
method: POST  
```
Create new user with username, password and email and logs in
```

```
POST /api/user/register HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json
```


### user account
api/user/account
method: GET  
```
Returns account_owner(username), account_number, account_balance
```

```
GET /api/user/account HTTP/1.1
Host: 127.0.0.1:8000
Cookie: sessionid=12345
```


### categories
api/categories
method: GET 
```
Returns category_type and category_name
```

```
GET /api/categories HTTP/1.1
Host: 127.0.0.1:8000
Cookie: sessionid=12345
```


### transaction latest
/api/transaction/latest  
method: GET  
```
Returns a list of transactions starting with the most recently added
```

```
GET /api/transaction/latest HTTP/1.1
Host: 127.0.0.1:8000
Cookie: sessionid=12345
```


### transaction filter
/api/transaction/filter  
method: GET  
```
Get filters:
 available filters:transaction_date, transaction_type, transaction_category, transaction_start_date + transaction_end_date
 /api/transaction/filter?transaction_date=2023-02-26 - return all user transaction on this date 2023-02-26
 /api/transaction/filter?transaction_type=Expense - return all user transaction with type=Expense
```

```
GET /api/transaction/filter?transaction_start_date=2023-02-01&transaction_end_date=2023-02-27&transaction_type=Expense&transaction_category=food HTTP/1.1
Host: 127.0.0.1:8000
Cookie: sessionid=12345
```

### transaction add
/api/transaction/add  
method: POST  
```
POST /api/transaction/add HTTP/1.1
Host: 127.0.0.1:8000
Cookie: sessionid=12345
Content-Type: application/json

{"transaction_type":"0", "transaction_category":"transport", "transaction_date": "2023-02-28", "transaction_sum": "20.00", "transaction_comment": "bus"}
```


### transaction delete
/api/transaction/\<int:transaction_id>/delete
method: POST  
```
POST /api/transaction/7/delete HTTP/1.1
Host: 127.0.0.1:8000
Cookie: sessionid=12345
Content-Type: application/json
```

### transaction statistic
/api/transaction/statistic 
method: GET  
```
Return transaction statistic for selection period
 api/transaction/statistic?transaction_start_date=2023-02-01&transaction_end_date=2023-02-27
```

```
GET /api/transaction/statistic?transaction_start_date=2023-02-01&transaction_end_date=2023-02-27 HTTP/1.1
Host: 127.0.0.1:8000
Cookie: sessionid=12345
```

### planned transactions
api/planning/planned_transactions
method: GET  
```
Returns a list of scheduled transactions
```

```
GET /api/planning/planned_transactions HTTP/1.1
Host: 127.0.0.1:8000
Cookie: sessionid=12345
```


### planned transaction add
/api/planning/transaction/add  
method: POST  
```
POST /api/planning/transaction/add  HTTP/1.1
Host: 127.0.0.1:8000
Cookie: sessionid=12345
Content-Type: application/json

{"transaction_type":"0", "transaction_category":"transport", "transaction_date": "2023-03-08", "transaction_sum": "200.00", "transaction_comment": "taxi"}
```


### planned transaction delete
api/planning/transaction/\<int:transaction_id>/delete
method: POST  
```
POST /api/planning/transaction/1/delete
Host: 127.0.0.1:8000
Cookie: sessionid=12345
Content-Type: application/json
```


###planned transaction statistic
/api/planning/transaction/statistic 
method: GET  
```
Returns the planned income and planned expense
```

```
GET /api/planning/transaction/statistic?transaction_start_date=2023-03-08&transaction_end_date=2023-03-15 HTTP/1.1
Host: 127.0.0.1:8000
Cookie: sessionid=12345
```
