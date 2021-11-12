import pymysql
import json
import logging

import middleware.context as context
from database_services.RDBService import RDBDataTable as RDBService

def get_form_data(form_id):
  conn = RDBService._get_db_connection()

  sql_statement = "select form_submission_id, col, col_val " \
      "from (marc1_db.forms join marc1_db.form_submission on marc1_db.forms.id=marc1_db.form_submission.form_id) join " \
    "marc1_db.form_submission_field_entry on marc1_db.form_submission.id=marc1_db.form_submission_field_entry.form_submission_id " \
    "where form_id=" + str(form_id) + ";"

  try:
      cur = conn.cursor()
      res = cur.execute(sql_statement, args=[])
      res = cur.fetchall()
  except Exception as e:
      conn.close()
      raise e

  return res
