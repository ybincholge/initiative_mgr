from pymongo import MongoClient

class DBUtil:
    def __init__(self, db_name):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client[db_name]

    def create(self, collection_name, data):
        collection = self.db[collection_name]
        result = collection.insert_one(data)
        return result.inserted_id

    def read(self, collection_name, query=None):
        collection = self.db[collection_name]
        if query is None:
            documents = collection.find()
        else:
            documents = collection.find(query)
        return [document for document in documents]

    def update(self, collection_name, query, new_values):
        collection = self.db[collection_name]
        result = collection.update_many(query, {'$set': new_values})
        return result.modified_count

    def delete(self, collection_name, query):
        collection = self.db[collection_name]
        result = collection.delete_many(query)
        return result.deleted_count

    def create_or_update(self, collection_name, query, new_values, data):
        collection = self.db[collection_name]
        if query:
            result = collection.update_one(query, {'$set': new_values})
            if result.matched_count == 0:
                result = collection.insert_one(data)
                return result.inserted_id
        else:
            result = collection.insert_one(data)
            return result.inserted_id
