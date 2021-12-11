# MARC 1 Form Hoster

[![Quality gate](https://sonarcloud.io/api/project_badges/quality_gate?project=martinristovski_marc1)](https://sonarcloud.io/summary/new_code?id=martinristovski_marc1)

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

You can run the System test suite from (https://columbia-university-student-plan-team-187884.postman.co/workspace/MARC-1~82207b09-c523-462c-b17e-3806dbfc9ecc/collection/1089331-e6d03ab1-7795-442f-a84f-5b795b1e3139).

Please select Production as Environment from the list of environments.

Run the collection Form-Hoster-IA-Demo.

## API Documentation

The API documentation is available at:

[https://documenter.getpostman.com/view/1089331/UVR4PqQU](https://documenter.getpostman.com/view/1089331/UVR4PqQU)


The openAPI documentation is committed at:
https://github.com/martinristovski/marc1/blob/main/api/openapi.yaml

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

## CI PIPELINE

We run our CI pipeline on every commit to the main branch
The pipeline does the followings

```
Runs flake8
Runs Unit Test cases
Generates Code coverage Report
Runs SonarCloud
Runs Postman Test Suite
Generates an HTML for Postman Test Suite
```

Flake8 and code coverage reports are present at
(https://github.com/martinristovski/marc1/tree/main/test-results)

SonarCloud report is present as a badge in the README ABOVE

The postman reports are present at
(https://github.com/martinristovski/marc1/tree/main/newman)


## SAMPLE REPORT

- CI PIPELINE
  - ![alt text](https://github.com/martinristovski/marc1/blob/main/sample_reports/Screen%20Shot%202021-12-11%20at%2011.48.39%20AM.png)
- FLAKE8
  - ![alt text](https://github.com/martinristovski/marc1/blob/main/sample_reports/Screen%20Shot%202021-12-11%20at%2011.49.04%20AM.png)
- COVERAGE
  - ![alt text](https://github.com/martinristovski/marc1/blob/main/sample_reports/Screen%20Shot%202021-12-11%20at%2011.49.54%20AM.png)
- SONARCLOUD
  - ![alt text](https://github.com/martinristovski/marc1/blob/main/sample_reports/Screen%20Shot%202021-12-11%20at%2011.45.04%20AM.png)
- POSTMAN
  - ![alt text](https://github.com/martinristovski/marc1/blob/main/sample_reports/Screen%20Shot%202021-12-11%20at%2011.49.29%20AM.png)
