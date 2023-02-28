### user login
/api/user/login  
method: POST  
```
POST /api/user/login HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json

{"username":"Dasha","password":"testpassword123"}
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
Content-Type: application/json

{"transaction_type":"0", "transaction_category":"transport", "transaction_date": "2023-02-28", "transaction_sum": "20.00", "transaction_comment": "bus"}
```


### transaction delete
/api/transaction/\<int:transaction_id>/delete
method: POST  
```
POST /api/transaction/7/delete HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json

```