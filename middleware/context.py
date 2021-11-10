
import os
import pymysql


def get_rdb_db_info():
    """
    :return: A dictionary with connect info for MySQL
    """
    db_host = os.environ.get("DBHOST", None)
    db_user = os.environ.get("DBUSER", None)
    db_password = os.environ.get("DBPASSWORD", None)
    

    if db_host is not None:
        db_info = {
            "host": db_host,
            "user": db_user,
            "password": db_password,
            "cursorclass": pymysql.cursors.DictCursor
        }
    else:
        db_info = {
            "host": "localhost",
            "user": "dbuser",
            "password": "dbuserdbuser",
            "cursorclass": pymysql.cursors.DictCursor
        }

    return db_info

def get_rdb_schema():
    """
    return: The name of the database to be used
    """
    return os.environ.get("RDBSCHEMA", None)

def get_mongo_db_info():
    db_host = os.environ.get("MONGO_DBHOST", None)
    db_connect_info = {
                "HOST": db_host,
                "PORT": 27017,
                "DB": "Forms"
    }
    return db_connect_info
