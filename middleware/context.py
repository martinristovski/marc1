
import os
import pymysql


def get_rdb_info():
    """
    :return: A dictionary with connect info for MySQL
    """
    
    db_host = os.environ.get("DBHOST", None)
    db_user = os.environ.get("DBUSER", None)
    db_password = os.environ.get("DBPASSWORD", None)
    schema_name = os.environ.get("RDBSCHEMA", None)

    if db_host is not None:
        db_info = {
            "host": db_host,
            "user": db_user,
            "password": db_password,
            "db": schema_name,
            "cursorclass": pymysql.cursors.DictCursor
        }
    else:
        db_info = {
            "host": "localhost",
            "user": "dbuser",
            "password": "dbuserdbuser",
            "db": schema_name,
            "cursorclass": pymysql.cursors.DictCursor
        }

    return db_info

def get_mongo_db_info():
    '''
    db_host = os.environ.get("MONGO_DBHOST", None)
    db_user = os.environ.get("MONGO_USER", None)
    db_pass = os.environ.get("MONGO_PASSWORD", None)
    
    db_connect_info = {
                "HOST": db_host,
                "USERNAME": db_user,
                "PASSWORD": db_pass,
                "PORT": 27017,
                "DB": "Forms"
    }
    '''
    db_url = os.environ.get("MONGO_URL", None)
    db_connect_info = {
                "URL": db_url,
                "PORT": 27017,
                "DB": "Forms"
    }
    return db_connect_info
