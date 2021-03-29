from database.mainshop import shop
from pymongo import MongoClient
import discord
import random
from models.item import Item
from os import environ
from database.admin import admins

cluster = MongoClient(environ.get('mongo_url'))


def scrambleWord(word):
    word = list(word)
    limit = len(word)
    scrambled = ''
    while len(scrambled) < limit:
        random_index = random.randint(0, len(word) - 1)
        scrambled += word[random_index]
        word.pop(random_index)

    return scrambled


async def auction(ctx, item="", price=0):
    if item == "":
        return await ctx.send("Please specify an item")
    if price <= 0:
        return await ctx.send("Please specify a valid price")
    db = cluster['main']
    collection = db['accounts']
    accounts = collection.find_one({'_id': 1})
    if not str(ctx.author.id) in accounts.keys():
        openAccount(ctx.author.id)
        return await ctx.send("You don't own any items.")
    user_bal = accounts[str(ctx.author.id)]
    for thing in shop:
        if thing.name.lower() == item.lower():
            if 'bag' not in user_bal.keys():
                return await ctx.send("You don't own any items.")
            if item.lower() not in user_bal['bag'].keys():
                return await ctx.send("You don't this item.")
            if user_bal['bag'][item.lower()]['amount'] < 1:
                return await ctx.send("You don't own this item.")
            market = db['market'].find_one({'_id': 3})
            item_id = random.randint(600000000000000000, 999999999999999999)
            item_model = Item(name=item.lower(), emoji=thing.emoji, item_id=item_id, price=int(price),
                              owner=ctx.author.id).to_dict()
            if 'items' not in market.keys():
                market['items'] = {}
            if item.lower() in market['items'].keys():
                market['items'][item.lower()].append(item_model)
            else:
                market['items'][item.lower()] = [item_model]
            collection = db['market']
            collection.update_one({'_id': 3}, {'$set': {'items': market['items']}})
            collection = db['accounts']
            if user_bal['bag'][item.lower()]['amount'] == 1:
                del user_bal['bag'][item.lower()]
            else:
                user_bal['bag'][item.lower()]['amount'] -= 1
            collection.update_one({'_id': 1}, {'$set': {str(ctx.author.id): user_bal}})
            await ctx.send(f"Your {item.lower()} has been **uploaded** to the market for `{int(price)}` coins.")


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
            "bank": 0,
            "credits": 0
        }
        collection.update_one({"_id": 1}, {"$set": {str(member_id): temp}})


def accountExists(member_id):
    db = cluster['main']
    collection = db['accounts']
    accounts = collection.find_one({'_id': 1})

    return str(member_id) in accounts.keys()


def balance(member_id):
    if not accountExists(member_id):
        openAccount(member_id)
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


def custom_sort(accounts: list, method='wallet', reverse=False):
    for i in range(len(accounts)):
        for j in range(len(accounts) - i - 1):
            if accounts[j][method] < accounts[j + 1][method]:
                temp = accounts[j]
                accounts[j] = accounts[j + 1]
                accounts[j + 1] = temp
    if reverse:
        accounts.reverse()

    return accounts


async def giftItem(ctx, user, item, amount=1):
    db = cluster['main']
    collection = db['accounts']
    accounts = collection.find_one({'_id': 1})
    if not 'bag' in accounts[str(ctx.author.id)].keys() or not item.lower() in accounts[str(ctx.author.id)][
        'bag'].keys():
        return await ctx.send("You do not have enough items.")
    if amount > accounts[str(ctx.author.id)]['bag'][item.lower()]:
        return await ctx.send("You do not have enough items.")

    if str(user.id) in accounts.keys():
        if 'bag' in accounts[str(user.id)].keys():
            if item.lower() in accounts[str(user.id)]['bag'].keys():
                accounts[str(user.id)]['bag'][item.lower()] += amount
            else:
                accounts[str(user.id)]['bag'][item.lower()] = amount
        else:
            accounts[str(user.id)]['bag'] = {}
            accounts[str(user.id)]['bag'][item.lower()] = amount
    else:
        openAccount(user.id)
        accounts = collection.find_one({'_id': 1})
        accounts[str(user.id)]['bag'] = {}
        accounts[str(user.id)]['bag'][item.lower()] = amount

    accounts[str(ctx.author.id)]['bag'][item.lower()] -= amount
    collection.update_one({'_id': 1}, {'$set': {str(user.id): accounts[str(user.id)]}})
    collection.update_one({'_id': 1}, {'$set': {str(ctx.author.id): accounts[str(ctx.author.id)]}})
    await ctx.send(f"**{ctx.author.display_name}** gave **{user.display_name}** `{amount}` {item.lower()}")


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
