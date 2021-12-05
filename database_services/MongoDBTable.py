from pymongo import MongoClient


class MongoDBTable:

    def __init__(self, table_name, connect_info=None,
                 key_columns=None, debug=True):
        """

        :param table_name: Name of the table.
            Subclasses interpret the exact meaning of table_name.
        :param connect_info: Dictionary of parameters
            necessary to connect to the data.
        :param key_columns: List, in order, of the
            columns (fields) that comprise the primary key.
            A primary key is a set of columns whose values
            are unique and uniquely identify a row.
        :param debug: If true, print debug messages.
        """
        self._connect_info = connect_info
        self._key_columns = key_columns
        self.table_name = table_name
        self._db = None
        self._mongo = None

        self._db = self._get_db()
        self._collection = self._db[table_name]

    def _get_key_string(self, row):
        result = []

        try:
            for k in self._key_columns:
                v = row[k]
                result.append(v)
            result = "_".join(result)
        except Exception as e:
            print("MongoDBTable._get_key_string: exception = ", e)
            raise KeyError("Could not form a key in for Mongo")

        return result

    def _get_db(self):

        if self._db is None:
            self._mongo = MongoClient(self._connect_info["URL"])
            self._db = self._mongo[self._connect_info["DB"]]

        return self._db


    def find_by_template(self, template, field_list=None,
                         limit=None, offset=None, order_by=None):
        """

        :param template: A dictionary of the form
            { "field1" : value1, "field2": value2, ...}. The function will
            return a derived table containing the rows that match the template.
        :param field_list: A list of requested fields
            of the form, ['fielda', 'fieldb', ...]
        :param limit: Do not worry about this for now.
        :param offset: Do not worry about this for now.
        :param order_by: Do not worry about this for now.
        :return: A derived table containing the computed rows.
        """
        result = []
        project = {}
        if field_list is not None:
            for f in field_list:
                project[f] = 1

        if project == {}:
            project = None

        res = self._collection.find(template, project)
        for r in res:
            result.append(r)

        return result

    def insert(self, new_record):
        """

        :param new_record: A dictionary representing a row to add to the set
            of records. Raises an exception if this
            creates a duplicate primary key.
        :return: None
        """
        print(new_record)
        k = self._get_key_string(new_record)
        print("keyString: " + str(k))
        new_record["primary_key"] = k
        res = self._collection.insert_one(new_record).inserted_id
        return res

    def delete_by_template(self, template):
        """

        Deletes all records that match the template.

        :param template: A template.
        :return: A count of the rows deleted.
        """
        result = self._collection.delete_many(filter=template)
        return result.deleted_count


