import json
from database.mainshop import shop
import pymongo
from pymongo import MongoClient
import discord

cluster = MongoClient(
    "mongodb+srv://dbBot:samarth1709@cluster0.moyjp.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

currencyPath = "database/currency.json"


def toTime(x: str):
    x = x.lower()
    if x.endswith('s'):
        return float(x[:-1])
    elif x.endswith('hr'):
        return float(x[:-2]) * 3600
    elif x.endswith('h'):
        return float(x[:-1]) * 3600
    elif x.endswith('m'):
        return float(x[:-1]) * 60
    elif x.endswith('min'):
        return float(x[:-3]) * 60


def timeConvertible(x: str):
    new = toTime(x)
    return not new is None


def openAccount(member_id):
    db = cluster['main']
    collection = db['accounts']
    accounts = collection.find_one({'_id': 1})
    if not str(member_id) in accounts.keys():
        temp = {
            "wallet": 2000,
            "bank": 0
        }
        collection.update_one({"_id": 1}, {"$set": {str(member_id): temp}})


def accountExists(member_id):
    db = cluster['main']
    collection = db['accounts']
    accounts = collection.find_one({'_id': 1})

    return str(member_id) in accounts.keys()


def balance(member_id):
    if not accountExists(member_id): openAccount(member_id)
    db = cluster['main']
    collection = db['accounts']
    accounts = collection.find_one({'_id': 1})

    return accounts[str(member_id)]


async def updateBalance(member_id, mode="wallet", amount=0):
    if not accountExists(member_id): openAccount(member_id)

    db = cluster['main']
    collection = db['accounts']
    accounts = collection.find_one({'_id': 1})

    bal = accounts[str(member_id)][mode]
    bal += amount
    if bal < 0:
        return False
    else:
        accounts[str(member_id)][mode] += amount
        collection.update_one({'_id': 1}, {'$set': {str(member_id): accounts[str(member_id)]}})

        return True


async def purchase(member_id, item: str, amount=1):
    bal = balance(member_id)
    db = cluster['main']
    collection = db['accounts']
    accounts = collection.find_one({'_id': 1})
    for thing in shop:
        if thing['name'] == item.lower():
            if bal['wallet'] >= thing['price'] * amount:
                if not 'bag' in accounts[str(member_id)].keys():
                    accounts[str(member_id)]['bag'] = {}
                    accounts[str(member_id)]['bag'][item.lower()] = amount
                    collection.update_one({'_id': 1}, {'$set': {str(member_id): accounts[str(member_id)]}})
                    await updateBalance(member_id, amount=int(-1 * amount * thing['price']))
                    return True
                elif not item.lower() in accounts[str(member_id)]['bag'].keys():
                    accounts[str(member_id)]['bag'][item.lower()] = amount
                    collection.update_one({'_id': 1}, {'$set': {str(member_id): accounts[str(member_id)]}})
                    await updateBalance(member_id, amount=int(-1 * amount * thing['price']))
                    return True
                elif item.lower() in accounts[str(member_id)]['bag'].keys():
                    accounts[str(member_id)]['bag'][item.lower()] += amount
                    collection.update_one({'_id': 1}, {'$set': {str(member_id): accounts[str(member_id)]}})
                    await updateBalance(member_id, amount=int(-1 * amount * thing['price']))
                    return True

    return False


async def showBagitems(ctx):
    db = cluster['main']
    collection = db['accounts']
    accounts = collection.find_one({'_id': 1})
    if not str(ctx.author.id) in accounts.keys(): return await ctx.send(
        "You don't own any items :eyes:. But some and use the command again")
    if not 'bag' in accounts[str(ctx.author.id)].keys(): return await ctx.send(
        "You don't own any items :eyes:. But some and use the command again")

    items = accounts[str(ctx.author.id)]['bag']
    des = f'**{ctx.author.display_name}\'s Bag**\n\n'
    for item in items:
        for thing in shop:
            if thing['name'] == item:
                des += f"{thing['emoji']} **{item} ─ ** {accounts[str(ctx.author.id)]['bag'][item]}\n*ID* `{item}` **─** Sellable\n\n"

    embed = discord.Embed(
        description=des,
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed)


async def sellItem(ctx, item, amount=1):
    db = cluster['main']
    collection = db['accounts']
    accounts = collection.find_one({'_id': 1})
    if not item.lower() in accounts[str(ctx.author.id)]['bag'].keys(): return await ctx.send("You don't own this item.")
    if accounts[str(ctx.author.id)]['bag'][item.lower()] == 0: return await ctx.send("You don't own this item.")
    if accounts[str(ctx.author.id)]['bag'][item.lower()] < amount: return await ctx.send("You don't own anough items")

    for thing in shop:
        if thing['name'] == item.lower():
            accounts[str(ctx.author.id)]['bag'][item.lower()] -= amount
            if accounts[str(ctx.author.id)]['bag'][item.lower()] == 0: del accounts[str(ctx.author.id)]['bag'][
                item.lower()]
            collection.update_one({'_id': 1}, {'$set': {str(ctx.author.id): accounts[str(ctx.author.id)]}})
            await updateBalance(ctx.author.id, amount=int(thing['price'] * 0.6 * amount))
            await ctx.send(
                f"You successfully sold `{amount}` {item.lower()} and earned `{int(thing['price'] * 0.6 * amount)}`")
