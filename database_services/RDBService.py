import pymysql
import copy         # Copy data structures.
import pymysql.cursors
from operator import itemgetter

import logging
logger = logging.getLogger()

# Maximum number of data rows to display in the __str__().
_max_rows_to_print = 10

cursorClass = pymysql.cursors.DictCursor
charset = 'utf8mb4'


class RDBDataTable:

    def __init__(self, table_name, connect_info, key_columns=None):
        """
        :param table_name: Name of the table.
            Subclasses interpret the exact meaning of table_name.
        :param connect_info: Dictionary of parameters
            necessary to connect to the data.
        :param key_columns: List, in order, of the
            columns (fields) that comprise the primary key.
            A primary key is a set of columns whose values
            are unique and uniquely identify a row.
        """
        self._table_name = table_name
        self._db_name = connect_info["db"]
        self._key_columns = key_columns
        self._connect_info = copy.deepcopy(connect_info)
        self._cnx = pymysql.connect(host=connect_info['host'],
                                    user=connect_info['user'],
                                    password=connect_info['password'],
                                    db=connect_info['db'],
                                    charset=charset,
                                    cursorclass=connect_info["cursorclass"])

        self._table_file = self._db_name + "." + self._table_name


    def run_q(self, q, args, cnx=None, cursor=None, commit=True, fetch=True):
        """

        :param q: The query string to run.
        :param fetch: True if this query produces a result and the function
        should perform and return fetchall()
        :return: result of the query
        """

        cursor_created = False
        cnx_created = False
        result = None

        try:
            if cnx is None:
                cnx = self._cnx
                cursor = self._cnx.cursor()
                cursor_created = True
            else:
                cnx = self._cnx
                cursor = cnx.cursor()
                cnx_created = True
                cursor_created = True

            log_message = cursor.mogrify(q, args)
            logger.debug(log_message)

            res = cursor.execute(q, args)

            if fetch:
                result = cursor.fetchall()
            else:
                result = res

            if commit:
                cnx.commit()
            if cursor_created:
                cursor.close()
            if cnx_created:
                cnx.close()
        except Exception as e:
            logger.warning("RDBDataTable.run_q, e = ", e)

            if commit:
                cnx.commit()
            if cursor_created:
                cursor.close()
            if cnx_created:
                cnx.close()

            raise e

        return result

    # Get the names of the columns
    def get_column_names(self):
        q = "show columns from " + self._table_name
        result = self.run_q(q, args=None, cnx=None, fetch=True)
        result = [r['Field'] for r in result]
        return list(result)

    # Get the number of rows
    def get_no_of_rows(self):
        q = "select count(*) as count from " + self._table_name
        result = self.run_q(q, args=None, cnx=None, fetch=True)
        result = result[0]['count']
        return result

    # Get the primary keys and indexes
    def get_key_columns(self):

        q = "show keys from " + self._table_name
        result = self.run_q(q, args=None, cnx=None, fetch=True)
        keys = [(r['Column_name'], r['Seq_in_index']) for r in result]
        keys = sorted(keys, key=itemgetter(1))
        keys = [k[0] for k in keys]
        return keys

    def template_to_where_clause(self, t):

        s = ""

        if t is None:
            return s

        for (k, v) in t.items():
            if s != "":
                s += " AND "
            s += k + "='" + v + "'"

        if s != "":
            s = "WHERE " + s

        return s

    def transfer_json_to_set_clause(self, t_json):

        args = []
        terms = []

        for k, v in t_json.items():
            args.append(v)
            terms.append(k + "=%s")

        clause = "set " + ", ".join(terms)

        return clause, args

    def find_by_template(self, t, fields=None, limit=None, offset=None):
        """
        The function will return a derived table containing
        the rows that match the template.

        :param t: A dictionary of the form
            { "field1" : value1, "field2": value2, ...}.
        :param fields: A list of requested fields of the form,
            ['fielda', 'fieldb', ...]
        :param limit: Nows of rows to return
        :param offset: Starting row to fetch from.
        :return: A derived table containing the computed rows.
        """

        w = self.template_to_where_clause(t)
        if fields is None:
            fields = ['*']
        q = "SELECT " + ",".join(fields) + \
            " FROM " + self._table_name + " " + w
        if limit is not None:
            q += " limit " + str(limit)
        if offset is not None:
            q += " offset " + str(offset)

        print("Query =", q)
        r = self.run_q(q, args=None, fetch=True)
        result = r
        print("Query result = ", r)
        return result

    def delete(self, template):
        """

        Deletes all records that match the template.

        :param template: A template.
        :return: A count of the rows deleted.
        """
        where_clause = self.template_to_where_clause(template)
        q1 = "delete from " + self._table_file + " " + where_clause + ";"
        q2 = "select row_count() as no_of_rows_deleted;"
        cursor = self._cnx.cursor()
        cursor.execute(q1)
        cursor.execute(q2)
        result = cursor.fetchone()
        self._cnx.commit()
        return result

    def insert(self, row):
        """

        :param row: A dictionary representing a
            row to add to the set of records.
        Raises an exception if this creates a duplicate primary key.
        :return: None
        """
        keys = row.keys()
        q = "INSERT into " + self._table_file + " "
        s1 = list(keys)
        s1 = ",".join(s1)

        q += "(" + s1 + ") "

        v = ["%s"] * len(keys)
        v = ",".join(v)

        q += "values(" + v + ")"

        params = tuple(row.values())

        result = self.run_q(q, params, fetch=False)

        return result

    def update(self, template, row):
        """

        :param template: A template that defines which matching rows to update.
        :param row: A dictionary containing fields
            and the values to set for the corresponding fields
            in the records. This returns an error if
            the update would create a duplicate primary key.
            NO ROWS are update on this error.
        :return: The number of rows updates.
        """
        set_clause, set_args = self.transfer_json_to_set_clause(row)
        where_clause = self.template_to_where_clause(template)

        q = "UPDATE  " + self._table_file + \
            " " + set_clause + " " + where_clause

        result = self.run_q(q, set_args, fetch=False)

        return result
