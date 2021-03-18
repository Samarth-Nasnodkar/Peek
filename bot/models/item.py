from models.errors import *
import pymongo
from pymongo import MongoClient
import random

cluster = MongoClient(
    "mongodb+srv://dbBot:samarth1709@cluster0.moyjp.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")


def openAccount(member_id):
    db = cluster['main']
    collection = db['accounts']
    accounts = collection.find_one({'_id': 1})
    if not str(member_id) in accounts.keys():
        temp = {
            "wallet": 2000,
            "bank": 0,
            "credits": 0
        }
        collection.update_one({"_id": 1}, {"$set": {str(member_id): temp}})


class Item:
    def __init__(self, name: str = None, emoji: str = None, item_id=None, amount=1, price=None, owner=None,
                 dict_form=None):
        if dict_form is None:
            self.item_id = item_id
            self.name = name[:1].upper() + name[1:].lower()
            self.emoji = emoji
            self.owner = owner
            self.price = price
            self.amount = amount
            self.dict_form = None
        else:
            self.dict_form = dict_form
            self.item_id = dict_form['item_id']
            self.name = dict_form['name'][:1].upper() + dict_form['name'][1:].lower()
            self.emoji = dict_form['emoji']
            self.owner = dict_form['owner']
            self.price = dict_form['price']
            self.amount = dict_form['amount']

    def __sub__(self, other):
        self.amount -= int(other)

    def __add__(self, other):
        self.amount += int(other)

    def to_dict(self):
        if self.dict_form is None:
            temp = {
                "item_id": self.item_id,
                "name": self.name.lower(),
                "emoji": self.emoji,
                "owner": self.owner,
                "price": self.price,
                "amount": self.amount
            }
            return temp
        return self.dict_form

    def sell(self, quantity=1):
        if self.amount < quantity:
            raise NotEnoughItemsError
        else:
            db = cluster['main']
            collection = db['accounts']
            accounts = collection.find_one({'_id': 1})
            accounts[str(self.owner)]['bag'][self.name.lower()]['amount'] -= quantity
            if accounts[str(self.owner)]['bag'][self.name.lower()]['amount'] == 0:
                del accounts[str(self.owner)]['bag'][self.name.lower()]
            accounts[str(self.owner)]['wallet'] += int(self.price * 0.6 * quantity)
            collection.update_one({'_id': 1}, {'$set': {str(self.owner): accounts[str(self.owner)]}})

    def buy(self, owner_id, quantity=1):
        db = cluster['main']
        collection = db['accounts']
        accounts = collection.find_one({'_id': 1})
        if str(owner_id) not in accounts.keys():
            openAccount(owner_id)
        accounts = collection.find_one({'_id': 1})
        if accounts[str(owner_id)]['wallet'] < quantity * self.price:
            raise NotEnoughBalanceError
        else:
            accounts[str(owner_id)]['wallet'] -= int(quantity * self.price)
            if 'bag' not in accounts[str(owner_id)].keys():
                accounts[str(owner_id)]['bag'] = {}
                item_id = random.randint(600000000000000000, 999999999999999999)
                accounts[str(owner_id)]['bag'][self.name.lower()] = Item(self.name.lower(), self.emoji, item_id,
                                                                         quantity, self.price, owner_id).to_dict()
            else:
                if self.name.lower() not in accounts[str(owner_id)]['bag'].keys():
                    item_id = random.randint(600000000000000000, 999999999999999999)
                    accounts[str(owner_id)]['bag'][self.name.lower()] = Item(self.name.lower(), self.emoji, item_id,
                                                                             quantity, self.price, owner_id).to_dict()
                else:
                    accounts[str(owner_id)]['bag'][self.name.lower()]['amount'] += quantity

            collection.update_one({'_id': 1}, {'$set': {str(owner_id): accounts[str(owner_id)]}})
