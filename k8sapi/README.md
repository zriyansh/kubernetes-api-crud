# k8s-crud

## APIS

### GET

http://127.0.0.1:8000/deploy/deploy-list

http://127.0.0.1:8000/deploy/apps/1/logs/



### POST
http://127.0.0.1:8000/deploy/
```
{
    "namespace": "example-namespace2",
    "application_name": "ahoy",
    "chart_name": "hello-world",
    "chart_version": "1.0.2"
}
```

http://127.0.0.1:8000/authen/login/
```
{
        "email": "testuser@example.com",
        "password": "Password@123"
}
```

http://127.0.0.1:8000/authen/signup/
```
{
        "username": "testuser2",
        "email": "testuser2@example.com",
        "password": "Password@123"
}
```

### DELETE
http://127.0.0.1:8000/deploy/apps/2/