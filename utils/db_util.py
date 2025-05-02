from pymongo import MongoClient

class DBUtil:
    def __init__(self, collection=None):
        self.client = MongoClient("10.157.75.217", 27017)
        self.db = self.client['iMgr']
        if collection:
            self.collection = self.db[collection]

    def setCollection(self, collection_name):
        self.collection = self.db[collection_name]

    def create(self, data):
        result = self.collection.insert_one(data)
        return result.inserted_id

    def read(self, query=None):
        if query is None:
            documents = self.collection.find()
        else:
            documents = self.collection.find(query)
        return [document for document in documents]

    def update(self, query, new_values):
        result = self.collection.update_many(query, {'$set': new_values})
        return result.modified_count

    def delete(self, query):
        result = self.collection.delete_many(query)
        return result.deleted_count

    def create_or_update(self, query, new_values, data):
        if query:
            result = self.collection.update_one(query, {'$set': new_values})
            if result.matched_count == 0:
                result = self.collection.insert_one(data)
                return result.inserted_id
        else:
            result = self.collection.insert_one(data)
            return result.inserted_id


def make_list_by_orgtype(list_org, filtered_org_type):
    return [k for k in list_org if 'type' in k and k['type']==filtered_org_type]


def make_list_by_field(s_list, field_name, add_first=None, add_last=None):
        result = [e[field_name] for e in s_list if field_name in e and e[field_name]]
        if add_last:
            result.append(add_last)
        if add_first:
            return result.insert(0, add_first)
        return result
