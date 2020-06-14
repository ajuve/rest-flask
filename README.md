# REST_FLASK

This utilities enable to generate a REST server with Python Flask and MySQL.

## Configure

You only have to configure the following parameters:

### Database parameters

| Parameter| Description |
|--|--|
| host="localhost"| Set the IP of the database host.|
| user="root"| Set the user of MySQL.|
| passwd=""| Set the password of MySQL.|
| database="erp"| Set the database name.|

### REST server parameters
| Parameter| Description |
|--|--|
| app.host = '0.0.0.0'| Set the IP of REST server.|
| app.port = 80| Set the Port of REST server.|
| app.tables = ['departments','employees','foo']| Set the table names to do CRUD.|

### Security
| Parameter| Description |
|--|--|
| app.guest_enable = False | Enable guest access to the database.|
| app.guest_writable = False| Enable guest users to do insert, update and delete.|
| app.username = 'admin'| Set the username.|
| app.password = '12345'| Set the password.|
| app.debug = True| Enable or disable debug console.|

## Run server

### Prerequisites
Install the following dependences:

 - pip install flask
 - pip install passlib
 - pip install mysql-client
 - pip install mysql.connector 

### Execute
python res_flask.py

## Examples
You can execute the basic CRUD operations for select, insert, update and delete data. Use GET method for select, POST method for insert, DELETE method for remove and PUT method for update.

For insert and update operations you have to pass the json data to do that.  If you want to check the REST, you can use Postman app.

    [GET] https://localhost/departments 
    [GET] https://localhost/departments/1
    [GET] https://localhost/departments/count
    [POST] https://localhost/departments
    [DELETE] https://localhost/departments/1
    [PUT] https://localhost/departments   

