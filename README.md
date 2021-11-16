# MARC 1 Form Hoster

## Prerequisites

The following packages are required to run the application:

- Python v3.8
- MySQL v8.0
- MongoDB v4.4.3

## Installation Guide

- Python: [https://www.python.org/downloads/](https://www.python.org/downloads/)
- MySQL: [https://dev.mysql.com/doc/mysql-installation-excerpt/8.0/en/](https://dev.mysql.com/doc/mysql-installation-excerpt/8.0/en/)
- MongoDB: [https://docs.mongodb.com/manual/administration/install-community/](https://docs.mongodb.com/manual/administration/install-community/)

## Build and Run Application

### Checkout code from the main branch:

```
git clone https://github.com/martinristovski/marc1.git
```

### Set up virtual environment:

```
python3 -m pip install --user virtualenv
python3 -m venv venv
```

### Install dependencies:

```
python3 -m pip install flask
python3 -m pip install coverage
python3 -m pip install flake8
source venv/bin/activate
pip install -r requirements.txt
```

### Configure environment variables:

```
export DBUSER=Username of MySQL (Ex:marc1_dev)
export DBPASSWORD=Password of MySQL user (Ex: marc1)
export DBHOST=Hostname of MySQL DB (fern.c5hb0sp2qrhh.us-east-2.rds.amazonaws.com)
export RDBSCHEMA=Name of the database (marc1_db)
export MONGO_URL= mongodb+srv://<username>:<password>@<hostname>/<dbName>?retryWrites=true&w=majority
(mongodb+srv://admin_marc1:marc1@cluster0.90pjm.mongodb.net/Form?retryWrites=true&w=majority)
```

### Migrate database:

```
mysql -u $DBUSER -p $DBPASSWORD  <  schema.sql
```

### Create MySQL User:

```
mysql -u $DBUSER -p $DBPASSWORD

create user ‘marc1_dev’@‘localhost' identified by ‘marc1’;
GRANT ALL PRIVILEGES ON marc1_db.* TO 'marc1_dev'@'%';
FLUSH PRIVILEGES;
```

### Run the application:

```
python app.py
```

### Check if the application is running:

```
curl -iv “http://127.0.0.1:5000/health”
```

The above API call should give a successful response, demonstrating that the application is running.

## Running the Test Suite

### API Testing

You can run the System test suite from [https://columbia-university-student-plan-team-187884.postman.co/workspace/82207b09-c523-462c-b17e-3806dbfc9ecc/overview](https://columbia-university-student-plan-team-187884.postman.co/workspace/82207b09-c523-462c-b17e-3806dbfc9ecc/overview).

Please select Production as Environment from the list of environments.

Run the collection Form-Hoster-Test.

The following should be the result of the test suite:

![image0](https://imgur.com/gsNgA7G.png)
![image1](https://imgur.com/T7PxOzg.png)
![image2](https://imgur.com/6i6iroq.png)
![image3](https://imgur.com/71U4C3V.png)

## API Documentation

The API documentation is available at:

[https://documenter.getpostman.com/view/1089331/UVC9gkPv](https://documenter.getpostman.com/view/1089331/UVC9gkPv)

In Postman, the API documentation is present at:
 
[https://columbia-university-student-plan-team-187884.postman.co/workspace/82207b09-c523-462c-b17e-3806dbfc9ecc/api/174189c9-7309-4fa9-bcf8-30052593bcc1/version/e8e717e9-80f6-4464-8310-c652996a22a5](https://columbia-university-student-plan-team-187884.postman.co/workspace/82207b09-c523-462c-b17e-3806dbfc9ecc/api/174189c9-7309-4fa9-bcf8-30052593bcc1/version/e8e717e9-80f6-4464-8310-c652996a22a5)

The openAPI documentation is committed at:

[https://github.com/martinristovski/marc1/blob/main/api/openapi.yaml](https://github.com/martinristovski/marc1/blob/main/api/openapi.yaml)

## Unit Testing

Checkout the code from the main branch:

[https://github.com/martinristovski/marc1](https://github.com/martinristovski/marc1)

Create a mysql server.

You can run all unit tests with the command:

```
python -m unittest
```

## Coverage

```
coverage run -m unittest discover
coverage report
```

![image4](https://imgur.com/NvI63MH.png)

## Static Code Analysis

To run the static code analysis tool, checkout the code from the main branch:

[https://github.com/martinristovski/marc1](https://github.com/martinristovski/marc1)

Make sure flake8 is installed in the system.

And run the below commands:

```
cd ..
flake8 marc1 > flake8.txt
```

An empty flake8.txt demonstrates that all the errors have been rectified.

![image5](https://imgur.com/Ojo8EUW.png)
