import discord
from discord.ext import commands
from cogs.helpers import *
from datetime import datetime
import random
from database.mainshop import shop
import asyncio
from pymongo import MongoClient
import time


class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.cluster = MongoClient(
    "mongodb+srv://dbBot:samarth1709@cluster0.moyjp.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

    @commands.command()
    async def market(self, ctx, search=""):
        if search == "":
            db = self.cluster['main']
            collection = db['market']
            market = collection.find_one({'_id': 3})
            items = list(market['items'].keys())
            items.sort()
            content = '**Global Market**\n\n'
            for item in items:
                item_models = market['items'][item]
                for i in range(len(item_models)):
                    for thing in shop:
                        if thing['name'] == item:
                            content += f"{thing['emoji']} **{item}   |**  price: `{item_models[i]['price']}`  **|**  No: `{item_models[i]['id']}`\n"

            embed = discord.Embed(
                description=content,
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)

    @commands.command()
    async def remove(self, ctx, item_id=0):
        if item_id == 0:
            return await ctx.send("Please specify a valid ID")
        db = self.cluster['main']
        collection = db['market']
        market = collection.find_one({'_id': 3})
        items = market['items']
        itemCollection = db['accounts'].find_one({'_id': 1})
        item_name = ''
        for item in list(items.keys()):
            i = 0
            while i < len(items[item]):
                if items[item][i]['id'] == item_id and items[item][i]['owner'] == ctx.author.id:
                    item_name = item
                    if item not in itemCollection[str(ctx.author.id)]['bag']:
                        itemCollection[str(ctx.author.id)]['bag'][item] = 1
                        items[item].pop(i)
                    else:
                        itemCollection[str(ctx.author.id)]['bag'][item] += 1
                        items[item].pop(i)

                i += 1

        db['accounts'].update_one({'_id': 1}, {'$set': {str(ctx.author.id): itemCollection[str(ctx.author.id)]}})
        collection.update_one({'_id': 3}, {'$set': {'items': market['items']}})
        await ctx.send(f"Your {item_name} has been **removed** from the market successfully.")

    @commands.command()
    async def auction(self, ctx, item="", price=0):
        if item == "":
            return await ctx.send("Please specify an item")
        if price <= 0:
            return await ctx.send("Please specify a valid price")
        db = self.cluster['main']
        collection = db['accounts']
        accounts = collection.find_one({'_id': 1})
        if not str(ctx.author.id) in accounts.keys():
            openAccount(ctx.author.id)
            return await ctx.send("You don't own any items.")
        user_bal = accounts[str(ctx.author.id)]
        for thing in shop:
            if thing['name'] == item.lower():
                if 'bag' not in user_bal.keys():
                    return await ctx.send("You don't own any items.")
                if item.lower() not in user_bal['bag'].keys():
                    return await ctx.send("You don't this item.")
                if user_bal['bag'][item.lower()] < 1:
                    return await ctx.send("You don't own this item.")
                market = db['market'].find_one({'_id': 3})
                item_id = random.randint(600000000000000000, 999999999999999999)
                item_model = {
                    'owner': ctx.author.id,
                    'id': item_id,
                    'type': item.lower(),
                    'price': int(price)
                }
                if 'items' not in market.keys():
                    market['items'] = {}
                if item.lower() in market['items'].keys():
                    market['items'][item.lower()].append(item_model)
                else:
                    market['items'][item.lower()] = [item_model]
                collection = db['market']
                collection.update_one({'_id': 3}, {'$set': {'items': market['items']}})
                collection = db['accounts']
                if user_bal['bag'][item.lower()] == 1:
                    del user_bal['bag'][item.lower()]
                else:
                    user_bal['bag'][item.lower()] -= 1
                collection.update_one({'_id': 1}, {'$set': {str(ctx.author.id): user_bal}})
                await ctx.send(f"Your {item.lower()} has been **uploaded** to the market for `{int(price)}` coins.")

    @commands.command(aliases=['balance'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def bal(self, ctx, user: discord.Member = None):
        if user is None: user = ctx.author

        bal = balance(user.id)
        embed = discord.Embed(
            title=f"{user.display_name}'s Balance",
            description=f":dollar:**Wallet** : `{bal['wallet']}` coins\n:bank:**Bank** : `{bal['bank']}` coins\n:tickets:**Credits** : `{bal['credits']}`\n\n",
            color=discord.Color.orange()
        )
        embed.set_footer(text=f"Command ran by {ctx.author.display_name}")
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)

    @bal.error
    async def bal_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = 'Command on cooldown for {:.2f}s'.format(error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def beg(self, ctx):
        earned = random.randint(50, 600)
        if await updateBalance(ctx.author.id, "wallet", amount=earned):
            await ctx.send(f"You earned {earned} coins")

    @beg.error
    async def beg_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = 'Command on cooldown for {:.2f}s'.format(error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    @commands.command()
    async def shop(self, ctx):
        description = ""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        for item in shop:
            description += f"{item['emoji']}**{item['name']}** - [⏣ {item['price']}]({url})\n"

        embed = discord.Embed(
            title="*__Shop Items__*",
            description=description,
            color=discord.Color.orange()
        )

        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def buy(self, ctx, item, amount=1):
        transaction = await purchase(ctx.author.id, item, amount)
        if transaction: return await ctx.send(f"Successfully purchased `{amount}` {item.lower()}")
        return await ctx.send('Purchase failed.')

    @commands.command(aliases=['inv', 'inventory'])
    async def bag(self, ctx):
        await showBagitems(ctx)

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def sell(self, ctx, item, amount=1):
        await sellItem(ctx, item, amount)

    @commands.command(aliases=['deposit'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def dep(self, ctx, amount=""):
        if amount == "": return await ctx.send("Please specify an amount")
        db = cluster['main']
        collection = db['accounts']
        accounts = collection.find_one({'_id': 1})
        if amount.lower() == "all":
            await updateBalance(ctx.author.id, amount=-1 * accounts[str(ctx.author.id)]['wallet'])
            await updateBalance(ctx.author.id, "bank", amount=accounts[str(ctx.author.id)]['wallet'])
            return await ctx.send(f"Successfully deposited `{accounts[str(ctx.author.id)]['wallet']}` coins")
        else:
            try:
                amt = int(amount)
                if amt > accounts[str(ctx.author.id)]['wallet']:
                    return await ctx.send("You do not have enough coins")

                await updateBalance(ctx.author.id, amount=-1 * amt)
                await updateBalance(ctx.author.id, "bank", amount=1 * amt)
                await ctx.send(f"Successfully deposited `{amt}` coins")
            except ValueError:
                return await ctx.send(f"Please specify a valid amount.")

    @dep.error
    async def dep_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = 'Command on cooldown for {:.2f}s'.format(error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    @commands.command(aliases=['with'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def withdraw(self, ctx, amount=""):
        if amount == "": return await ctx.send("Please specify an amount")
        db = cluster['main']
        collection = db['accounts']
        accounts = collection.find_one({'_id': 1})
        if amount.lower() == "all":
            await updateBalance(ctx.author.id, amount=accounts[str(ctx.author.id)]['bank'])
            await updateBalance(ctx.author.id, "bank", amount=-1 * accounts[str(ctx.author.id)]['bank'])
            return await ctx.send(f"Successfully withdrew `{accounts[str(ctx.author.id)]['bank']}` coins")
        else:
            try:
                amt = int(amount)
                if amt > accounts[str(ctx.author.id)]['bank']:
                    return await ctx.send("You do not have enough coins")

                await updateBalance(ctx.author.id, amount=amt)
                await updateBalance(ctx.author.id, "bank", amount=-1 * amt)
                await ctx.send(f"Successfully withdrew `{amt}` coins")
            except ValueError:
                return await ctx.send(f"Please specify a valid amount.")

    @withdraw.error
    async def with_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = 'Command on cooldown for {:.2f}s'.format(error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def rob(self, ctx, user: discord.Member = None):
        if user is None: return await ctx.send("Please specify a user.")
        userBal = balance(ctx.author.id)
        if userBal['wallet'] < 500: return await ctx.send('You need at least 500 coins to rob someone.')
        failureProb = random.randint(1, 8)
        success = False
        if failureProb == 3:
            success = True
        else:
            failureProb = float(failureProb / 7)
        failures = [
            f'You tried to rob {user.display_name} but the police caught you. You lost {int(failureProb * 500)} coins',
            f'You tried to rob {user.display_name} but there was a massive lock on their door. You lost {int(failureProb * 500)} coins',
            f'You tried to rob {user.display_name} but you forgot to carry your tools. You lost {int(failureProb * 500)} coins'
        ]
        if not success:
            await updateBalance(ctx.author.id, amount=-1 * int(failureProb * 500))
            print(f'{ctx.author} failed to rob {user}')
            return await ctx.send(random.choice(failures))

        robbedAmt = random.randint(balance(user.id))
        await updateBalance(ctx.author.id, amount=robbedAmt)
        await updateBalance(user.id, amount=-1 * robbedAmt)
        await ctx.send(f"You successfully robbed {robbedAmt} from {user.display_name}")
        print(f'{ctx.author} robbed {user}')

    @rob.error
    async def rob_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = 'Command on cooldown for {:.2f}s'.format(error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    @commands.command()
    async def give(self, ctx, user: discord.Member = None, amount=0):
        if user is None:
            return await ctx.send("Please specify a user.")
        if amount <= 0:
            return await ctx.send("Please specify a valid amount")
        if amount > balance(ctx.author.id)['wallet']:
            return await ctx.send('You do not have enough balance')
        await updateBalance(ctx.author.id, amount=-1 * amount)
        await updateBalance(user.id, amount=amount)
        return await ctx.send(f"**{ctx.author.display_name}** gave **{user.display_name}** `{amount}` coins")

    @commands.command(aliases=['transfer'])
    async def gift(self, ctx, user: discord.Member = None, item="", amount=1):
        if user is None:
            return await ctx.send("Please specify a user.")
        if item == "":
            return await ctx.send("Please specify a valid item")
        if amount <= 0:
            return await ctx.send("Please specify a valid amount")
        found = False
        for thing in shop:
            if thing['name'] == item.lower():
                found = True
                await giftItem(ctx, user, item, amount)

        if not found:
            await ctx.send("Please specify a valid item")

    @commands.command()
    async def heist(self, ctx, user: discord.Member = None):
        if user is None:
            return await ctx.send('Please specify a user')
        if balance(ctx.author.id)['wallet'] < 2000:
            return await ctx.send('You need atleast 2000 coins to heist someone.')
        if balance(user.id)['bank'] < 2000:
            return await ctx.send(f"{user.display_name} has very less money. Heist some rich person.")

        heistEmbed = discord.Embed(
            title=f"Bank heist against {user}",
            description=f"To take part in the above heist react below with the :bank: emoji.\nYou need at least 2000 coins to participate",
            color=discord.Color.orange()
        )
        heisters = []

        emb = await ctx.send(embed=heistEmbed)
        await emb.add_reaction('🏦')
        await asyncio.sleep(10)
        newMsg = await ctx.channel.fetch_message(emb.id)
        reactions = newMsg.reactions
        text = ''
        for reaction in reactions:
            if str(reaction.emoji) == '🏦':
                users = await reaction.users().flatten()
                for usr in users:
                    if usr.id != 819946835485261825 and balance(usr.id) > 2000:
                        heisters.append(usr.id)
                        text += f"**{usr.name}** , "

        text = text[:-2] + f"have teamed up for a heist against **{user}**"
        await ctx.send(text)
        await asyncio.sleep(2)
        won = random.randint(0, 4)
        print(won)
        if won == 2:
            totalWonAmt = random.randint(50, 101) * balance(user.id)['bank'] / 100
            individualWonAmt = int(totalWonAmt / len(heisters))
            content = ''
            for heister in heisters:
                content += f"{heister.display_name} won {individualWonAmt}\n"
                await updateBalance(heister.id, amount=individualWonAmt)
            await updateBalance(user.id, mode='bank', amount=-1 * int(individualWonAmt * len(heisters)))
            await ctx.send(
                f"You heisted {user.display_name} and took away {int(individualWonAmt * len(heisters))} coins")
            return await ctx.send(content)
        else:
            for heister in heisters:
                await updateBalance(heister, amount=-2000)

            await updateBalance(user.id, amount=2000 * len(heisters))
            return await ctx.send("Heist failed.\n**F**")

    @commands.command()
    async def slots(self, ctx, amount=""):
        if amount == "":
            return await ctx.send("Please specify an amount")
        if 'credits' not in balance(ctx.author.id).keys():
            return await ctx.send("You do not have any casino credits to bet. Please buy some using `credits` command.")
        if balance(ctx.author.id)['credits'] <= 0:
            return await ctx.send("You do not have any casino credits to bet. Please buy some using `credits` command.")
        if amount.lower() == "all":
            amount = balance(ctx.author.id)['credits']
        else:
            try:
                amount = int(amount)
            except ValueError:
                return await ctx.send("Please specify a valid amount")
        outcomes = []
        index = 0
        while index < 3:
            outcomes.append(random.randint(1, 25))
            index += 1
        embed = discord.Embed(
            title=f"Welcome to The Casino!",
            description="In slots, we will generate a random number thrice between 1 and 25. If you get two same "
                        "numbers,You win!.\nBe sure to buy some casino credits first.\n`1 coin = 3 credits`",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        for _ in outcomes:
            await ctx.send(f"**{_}**")
            await asyncio.sleep(1)
        if outcomes[0] == outcomes[1] or outcomes[2] == outcomes[1] or outcomes[0] == outcomes[2]:
            won_amt = int(random.randint(60, 150) * amount / 100)
            await updateBalance(ctx.author.id, mode="credits", amount=won_amt)
            await ctx.send(f"You won `{won_amt}` casino credits")
        else:
            await updateBalance(ctx.author.id, mode="credits", amount=-1 * amount)
            await ctx.send(f"You lost `{amount}` casino credits.")

    @commands.command()
    async def credits(self, ctx, mode="", amount=""):
        if mode.lower() == "buy":
            if amount.lower() == "all":
                amount = balance(ctx.author.id)['wallet'] * 3
            else:
                try:
                    amount = int(amount)
                except ValueError:
                    return await ctx.send("Please specify a valid amount")
        elif mode.lower() == 'sell':
            if amount.lower() == "all":
                amount = balance(ctx.author.id)['credits']
            else:
                try:
                    amount = int(amount)
                except ValueError:
                    return await ctx.send("Please specify a valid amount")

        if mode == "":
            return await ctx.send('Please use the command correctly. `credits <buy/sell> <amount>`')
        if amount <= 0:
            return await ctx.send("Please specify a valid amount.")
        if balance(ctx.author.id)['wallet'] < int(amount / 3) and mode.lower() == 'buy':
            return await ctx.send(f"You do not have enough coins to buy `{amount}` credits")
        if balance(ctx.author.id)['credits'] < amount and mode.lower() == 'sell':
            return await ctx.send("You do not have enough credits")

        if mode.lower() == 'buy':
            await updateBalance(ctx.author.id, amount=-1 * int(amount / 3))
            await updateBalance(ctx.author.id, mode="credits", amount=amount)
            await ctx.send(f"You successfully purchased `{amount}` coins.")
        elif mode.lower() == 'sell':
            await updateBalance(ctx.author.id, amount=int(amount / 3))
            await updateBalance(ctx.author.id, mode="credits", amount=-1 * amount)
            await ctx.send(f"You successfully sold `{amount}` coins.")


def setup(client):
    client.add_cog(Economy(client))
