from pymongo import MongoClient, errors
from pymongo.cursor import Cursor
from bson import ObjectId
from typing import Optional, Union, Dict


class DataBase:
    def __init__(self, db_url: str, db_name: str):
        try:
            self.client = MongoClient(db_url)
        except errors.ConnectionFailure:
            exit('Can\'t connect to server!')

        self.db = self.client[db_name]

    def add_user(self, user_id: int) -> str:
        return self.db.users.insert_one({'user_id': user_id}).inserted_id

    def get_user(self, user_id: Optional[int]=None) -> Union[Cursor, Dict]:
        if user_id:
            return self.db.users.find_one({'user_id': user_id})

        return self.db.users.find({})

    def edit_user(self, user_id: int, data: dict) -> int:
        return self.db.users.update_one({'user_id': user_id}, {'$set': data}).modified_count

    def delete_user(self, user_id: Optional[int]=None) -> int:
        if user_id:
            result = self.db.users.delete_many({})
        else:
            result = self.db.users.delete_one({'user_id': user_id})

        return result.deleted_count

    def add_account(self, user_id: int, username: str, sh_sc: str) -> str:
        return self.db.accounts.insert_one({'user_id': user_id, 'username': username, 'sh_sc': sh_sc}).inserted_id

    def get_account(self, _id: Optional[str]=None, user_id: Optional[int]=None, username: Optional[str]=None) -> Union[Cursor, Dict]:
        if _id:
            filter = {'_id': ObjectId(_id)}
            func = self.db.accounts.find_one
        elif user_id and username:
            filter = {'user_id': user_id, 'username': username}
            func = self.db.accounts.find_one
        elif user_id:
            filter = {'user_id': user_id}
            func = self.db.accounts.find
        elif username:
            filter = {'username': username}
            func = self.db.accounts.find_one
        else:
            filter = {}
            func = self.db.accounts.find

        return func(filter)

    def delete_account(self, user_id: Optional[int]=None, username: Optional[str]=None) -> int:
        if user_id and username:
            filter = {'user_id': user_id, 'username': username}
            func = self.db.accounts.delete_one
        else:
            filter = {}
            func = self.db.accounts.delete_many

        return func(filter).deleted_count
