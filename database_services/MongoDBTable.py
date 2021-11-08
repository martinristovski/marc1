from pymongo import MongoClient


class MongoDBTable:

    def __init__(self, table_name, connect_info=None, key_columns=None, debug=True):
        """

        :param table_name: Name of the table. Subclasses interpret the exact meaning of table_name.
        :param connect_info: Dictionary of parameters necessary to connect to the data. See examples in subclasses.
        :param key_columns: List, in order, of the columns (fields) that comprise the primary key.
            A primary key is a set of columns whose values are unique and uniquely identify a row. For Appearances, the columns are ['playerID', 'teamID', 'yearID']
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
            self._mongo = MongoClient(
                host=self._connect_info["HOST"],
                port=self._connect_info["PORT"]
            )
            self._db = self._mongo[self._connect_info["DB"]]

        return self._db

    def find_by_primary_key(self, key_fields, field_list=None):
        """

        :param key_fields: The values for the key_columns, in order, to use to find a record. For example, for Appearances this could be ['willite01', 'BOS', '1960']
        :param field_list: A subset of the fields of the record to return. The table may have many additional columns, but the caller only requests this subset.
        :return: None, or a dictionary containing the requested columns/values for the row.
        """
        p_key = "_".join(key_fields)
        res = self._collection.find_one({"primary_key": p_key})
        return res

    def find_by_template(self, template, field_list=None, limit=None, offset=None, order_by=None):
        """

        :param template: A dictionary of the form { "field1" : value1, "field2": value2, ...}. The function will return a derived table containing the rows that match the template.
        :param field_list: A list of requested fields of the form, ['fielda', 'fieldb', ...]
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

        :param new_record: A dictionary representing a row to add to the set of records. Raises an exception if this
            creates a duplicate primary key.
        :return: None
        """
        k = self._get_key_string(new_record)
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

    def delete_by_key(self, key_fields):
        """

        Deletes the record that match the key values.

        :param key_fields: List containing the values for the key columns
        :return: A count of the rows deleted.
        """
        p_key = "_".join(key_fields)
        res = self._collection.delete_many({"primary_key": p_key})
        return res.deleted_count

    def update_by_template(self, template, new_values):
        """

        :param template: A template that defines which matching rows to update.
        :param new_values: A dictionary containing fields and the values to set for the corresponding fields
            in the records. This returns an error if the update would create a duplicate primary key. NO ROWS are
            update on this error.
        :return: The number of rows updates.
        """
        res = self._collection.update_many(filter=template, update=new_values)
        return res.modified_count

    def update_by_key(self, key_fields, new_values):
        """

        :param key_fields: List of values for primary key fields
        :param new_values: A dictionary containing fields and the values to set for the corresponding fields
            in the records. This returns an error if the update would create a duplicate primary key. NO ROWS are
            update on this error.
        :return: The number of rows updates.
        """
        p_key = "_".join(key_fields)
        print(p_key)
        res = self._collection.update_one({"primary_key": key_fields}, {'$set': new_values}, upsert=True)
        print("Modified count [" + str(res.modified_count) + "]")
        return res.modified_count

    def find_by_pattern(self, template, fields):
        if template is None:
            return self.find_by_template(template, fields)

        is_proceed = False
        for key, items in template.items():
            if 'children' in key:
                is_proceed = True

        if not is_proceed:
            return self.find_by_template(template, fields)

        result = []
        pipeline_list = []
        pipeline = {'$match': template}
        pipeline_list.append(pipeline)

        filter_hash = {'input': '$children', 'as': 'children'}

        eq_list = []
        cond_hash = {}
        for key, value in template.items():
            print("Key:" + str(key))
            print("Val:" + str(value))

            if 'children.tags' in key:
                eq_list.append(value)
                key_str = '$$' + str(key)
                eq_list.append(key_str)
                cond_hash['$in'] = eq_list
            elif 'children' in key:

                key_str = '$$' + str(key)
                # key_list = [key_str]
                eq_list.append(key_str)
                eq_list.append(value)
                cond_hash['$eq'] = eq_list

        filter_hash['cond'] = cond_hash
        children_hash = {'$filter': filter_hash}
        project_hash = {'children': children_hash}
        project = {'$project': project_hash}
        pipeline_list.append(project)

        unwind_hash = {'path': '$children'}
        unwind = {'$unwind': unwind_hash}
        pipeline_list.append(unwind)

        project_hash = {'post_id': '$children.post_id', 'comment_id': '$children.comment_id',
                        'response_date': '$children.response_date', 'text': '$children.response_text',
                        'tags': '$children.tags', 'email': '$children.email'}

        project = {'$project': project_hash}
        pipeline_list.append(project)

        print(str(pipeline_list))
        res = self._collection.aggregate(pipeline_list)
        for r in res:
            result.append(r)
        return result
