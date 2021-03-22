import discord
from discord.ext import commands
from cogs.helpers import *
from datetime import datetime
import random
from database.mainshop import shop
import asyncio
from models.item import Item
from pymongo import MongoClient
from models.errors import *
from models.trade import Trade


class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.cluster = MongoClient(
            "mongodb+srv://dbBot:samarth1709@cluster0.moyjp.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

    @commands.command(aliases=['m'])
    async def market(self, ctx, arg="search", search="", price=0):
        if arg.lower() == "search":
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
                        item_model = Item(dict_form=item_models[i])
                        content += f"{item_model.emoji} **{item_model}   |**  price: `{item_model.price}`  **|**  No:" \
                                   f" `{item_model.item_id}`\n"

                embed = discord.Embed(
                    description=content,
                    color=discord.Color.orange()
                )
                await ctx.send(embed=embed)
            else:
                db = self.cluster['main']
                collection = db['market']
                market = collection.find_one({'_id': 3})
                items = list(market['items'].keys())
                if search.lower() not in items:
                    for _model in shop:
                        if _model.name.lower() == search.lower():
                            return await ctx.send(f"No **{_model}** in the shop right now.")

                    return await ctx.send("Please enter a valid item.")
                content = f'**Search results for {search[:1].upper() + search[1:].lower()}**\n\n'
                item_models = market['items'][search.lower()]
                for _model in item_models:
                    item_model = Item(dict_form=_model)
                    content += f"{item_model.emoji} **{item_model}   |**  price: `{item_model.price}`  **|**  No:" \
                               f" `{item_model.item_id}`\n"
                embed = discord.Embed(
                    description=content,
                    color=discord.Color.orange()
                )
                await ctx.send(embed=embed)
        elif arg.lower() == "add" or arg.lower() == "a":
            await auction(ctx, search.lower(), price)
        elif arg.lower() == "remove" or arg.lower() == "r":
            try:
                await self.remove(ctx, item_id=int(search))
            except ValueError:
                await ctx.send("Please enter a valid item id")

    @commands.command()
    async def trade(self, ctx, user: discord.Member = None):
        if user is None:
            return await ctx.send("Please specify a valid user.")

        await ctx.send(f"{user.mention} Do you accept the trade?")
        yn = ['yes', 'no']

        def trade_accept(message):
            return message.channel == ctx.channel and message.author == user and message.content.lower() in yn

        try:
            msg = await self.client.wait_for('message', timeout=30.0, check=trade_accept)
        except asyncio.TimeoutError:
            return await ctx.send(f"{user.mention} You did not respond in 30s, trade ended.")
        else:
            if msg.content.lower() == 'no':
                return await ctx.send("Trade ended.")

            author_trade = Trade(ctx.author)
            user_trade = Trade(user)
            des = f"Initiate the trade by adding an item or money\n`>coin (amount) ➜ To add coins` or\n" \
                  f"`>cred (amount) ➜ To add credits` or\n `>item (name) (amount) ➜ To add item.[Amount defaults to 1]`" \
                  f"\nConfirm the trade using `>confirm`"
            embed = discord.Embed(
                title=f"Trade between {ctx.author.display_name} and {user.display_name}",
                description=des,
                color=discord.Color.orange()
            )
            emb = await ctx.send(embed=embed)
            db = self.cluster['main']['accounts']
            collection = db.find_one({'_id': 1})
            if str(user.id) not in collection.keys():
                openAccount(user.id)
            if str(ctx.author.id) not in collection.keys():
                openAccount(ctx.author.id)

            def trading_cmds(message):
                return message.channel == ctx.channel and (message.author == user or message.author == ctx.author) and (
                        message.content.startswith('>cred') or message.content.startswith(
                    '>item') or message.content.startswith('>coin') or message.content.startswith('>confirm'))

            while True:
                try:
                    msg = await self.client.wait_for('message', timeout=30.0, check=trading_cmds)
                except asyncio.TimeoutError:
                    return await ctx.send(f"You took too long to add items. Trade ended.")
                else:
                    if msg.content.startswith('>confirm'):
                        if msg.author == ctx.author:
                            if author_trade.confirmed:
                                await ctx.send("You have already confirmed the trade.")
                            else:
                                author_trade.confirm()
                        else:
                            if user_trade.confirmed:
                                await ctx.send("You have already confirmed the trade.")
                            else:
                                user_trade.confirm()
                    else:
                        proceed = True
                        if msg.author == ctx.author:
                            if author_trade.confirmed:
                                proceed = False
                        elif msg.author == user:
                            if user_trade.confirmed:
                                proceed = False
                        if proceed:
                            content = msg.content.lower()
                            if content.startswith('>cred'):
                                try:
                                    amount = int(content[5:])
                                except ValueError:
                                    await ctx.send("Please specify a valid amount")
                                else:
                                    if amount > collection[str(msg.author.id)]['credits']:
                                        await ctx.send("You do not have this much money. Enter a valid amount")
                                    else:
                                        if msg.author == ctx.author:
                                            author_trade.add_credits(amount)
                                        else:
                                            user_trade.add_credits(amount)
                            elif content.startswith('>coin'):
                                try:
                                    amount = int(content[5:])
                                except ValueError:
                                    await ctx.send("Please specify a valid amount")
                                else:
                                    if amount > collection[str(msg.author.id)]['wallet']:
                                        await ctx.send("You do not have this much money. Enter a valid amount")
                                    else:
                                        if msg.author == ctx.author:
                                            author_trade.add_coins(amount)
                                        else:
                                            user_trade.add_coins(amount)
                            elif content.startswith('>item'):
                                try:
                                    words = content.split()
                                    if len(words) == 3:
                                        item_name = words[1]
                                        item_amount = int(words[2])
                                    else:
                                        item_name = words[1]
                                        item_amount = 1
                                except ValueError:
                                    await ctx.send("Please specify a valid amount")
                                else:
                                    try:
                                        if 'bag' not in collection[str(msg.author.id)].keys():
                                            await ctx.send('You do no own this item')
                                            raise NotEnoughItemsError
                                        if item_name.lower() not in collection[str(msg.author.id)]['bag'].keys():
                                            await ctx.send('You do no own this item')
                                            raise NotEnoughItemsError
                                        item_model = Item(
                                            dict_form=collection[str(msg.author.id)]['bag'][item_name.lower()])
                                        temp = 0
                                        if msg.author == ctx.author:
                                            for _model in author_trade.items:
                                                if _model.name.lower() == item_name.lower():
                                                    temp = _model.amount
                                                    break
                                        else:
                                            for _model in user_trade.items:
                                                if _model.name.lower() == item_name.lower():
                                                    temp = _model.amount
                                                    break
                                        if item_amount + temp > item_model.amount:
                                            await ctx.send("You do not own this many items.")
                                        else:
                                            if msg.author == ctx.author:
                                                present = False
                                                for _ in author_trade.items:
                                                    if _.name.lower() == item_name.lower():
                                                        _.amount += item_amount
                                                        present = True
                                                        break
                                                if not present:
                                                    addable_item = item_model.to_dict()
                                                    addable_item['amount'] = item_amount
                                                    addable_item = Item(dict_form=addable_item)
                                                    author_trade.add_items(addable_item)
                                            else:
                                                present = False
                                                for _ in user_trade.items:
                                                    if _.name.lower() == item_name.lower():
                                                        _.amount += item_amount
                                                        present = True
                                                        break
                                                if not present:
                                                    addable_item = item_model.to_dict()
                                                    addable_item['amount'] = item_amount
                                                    addable_item = Item(dict_form=addable_item)
                                                    user_trade.add_items(addable_item)
                                    except:
                                        pass
                        else:
                            await ctx.send("You cannot add an item after confirming the trade.")

                    if not author_trade.confirmed or not user_trade.confirmed:
                        des = f'```apache\n{ctx.author.display_name} is Offering\nItems: '
                        for item in author_trade.items:
                            des += f"{item} - {item.amount},"
                        des = des[:-1]
                        des += f"\nCredits: {author_trade.credits}\nCoins: {author_trade.coins}\nConfirmed: " \
                               f"{author_trade.cfe}\n```\n```apache" \
                               f"\n{user.display_name} is Offering\nItems: "
                        for item in user_trade.items:
                            des += f"{item} - {item.amount},"
                        des = des[:-1]
                        des += f"\nCredits: {user_trade.credits}\nCoins: {user_trade.coins}\nConfirmed: " \
                               f"{user_trade.cfe}\n```"
                        embed = discord.Embed(
                            description=des,
                            color=discord.Color.orange()
                        )
                        await emb.edit(embed=embed)
                    else:
                        for _model in author_trade.items:
                            try:
                                _model.transfer(user, _model.amount)
                            except NotEnoughItemsError:
                                await ctx.send(f"**{ctx.author.display_name}** do not have enough **{_model}**")
                        for _model in user_trade.items:
                            try:
                                _model.transfer(ctx.author, _model.amount)
                            except NotEnoughItemsError:
                                await ctx.send(f"**{user.display_name}** do not have enough **{_model}**")

                        if author_trade.credits > 0:
                            success = await updateBalance(ctx.author.id, "credits", -1 * author_trade.credits)
                            if success:
                                await updateBalance(user.id, "credits", author_trade.credits)
                            else:
                                await ctx.send(f"**{ctx.author.display_name}** do not have enough credits.")
                        if author_trade.coins > 0:
                            success = await updateBalance(ctx.author.id, "wallet", -1 * author_trade.coins)
                            if success:
                                await updateBalance(user.id, "wallet", author_trade.coins)
                            else:
                                await ctx.send(f"**{ctx.author.display_name}** do not have enough credits.")
                        if user_trade.credits > 0:
                            success = await updateBalance(user.id, "credits", -1 * user_trade.credits)
                            if success:
                                await updateBalance(ctx.author.id, "credits", user_trade.credits)
                            else:
                                await ctx.send(f"**{user.display_name}** do not have enough credits.")
                        if user_trade.coins > 0:
                            success = await updateBalance(user.id, "wallet", -1 * user_trade.coins)
                            if success:
                                await updateBalance(ctx.author.id, "wallet", user_trade.coins)
                            else:
                                await ctx.send(f"**{user.display_name}** do not have enough credits.")
                        return await ctx.send("Trade ended.")

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
                if items[item][i]['item_id'] == item_id and items[item][i]['owner'] == ctx.author.id:
                    item_name = item
                    if item not in itemCollection[str(ctx.author.id)]['bag'].keys():
                        itemCollection[str(ctx.author.id)]['bag'][item]['amount'] = 1
                        items[item].pop(i)
                    else:
                        itemCollection[str(ctx.author.id)]['bag'][item]['amount'] += 1
                        items[item].pop(i)

                i += 1

        db['accounts'].update_one({'_id': 1}, {'$set': {str(ctx.author.id): itemCollection[str(ctx.author.id)]}})
        collection.update_one({'_id': 3}, {'$set': {'items': market['items']}})
        await ctx.send(f"Your {item_name} has been **removed** from the market successfully.")

    @commands.command(aliases=['balance'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def bal(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author

        bal = balance(user.id)
        embed = discord.Embed(
            title=f"{user.display_name}'s Balance",
            description=f":dollar:**Wallet** : `{bal['wallet']}` coins\n:bank:**Bank** : `{bal['bank']}` coins"
                        f"\n:tickets:**Credits** : `{bal['credits']}`\n\n",
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
            description += f"{item.emoji}**{item.name}** - [⏣ {item.price}]({url})\n"

        embed = discord.Embed(
            title="*__Shop Items__*",
            description=description,
            color=discord.Color.orange()
        )

        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def buy(self, ctx, item, amount=1):
        # transaction = await purchase(ctx.author.id, item, amount)
        # if transaction: return await ctx.send(f"Successfully purchased `{amount}` {item.lower()}")
        # return await ctx.send('Purchase failed.')
        if amount <= 0:
            return await ctx.send("Please specify a valid amount")
        found = False
        for thing in shop:
            if thing.name.lower() == item.lower():
                found = True
                try:
                    thing.buy(ctx.author.id, amount)
                except NotEnoughBalanceError:
                    return await ctx.send(f"You do not have enough credits to buy this item.")
                else:
                    await ctx.send(f"You successfully purchased `{amount}` **{item[:1].upper() + item[1:].lower()}**")
                    break

        if not found:
            await ctx.send("Please specify a valid item")

    @commands.command(aliases=['inv', 'inventory'])
    async def bag(self, ctx):
        db = self.cluster['main']
        collection = db['accounts']
        accounts = collection.find_one({'_id': 1})
        if str(ctx.author.id) not in accounts.keys():
            openAccount(ctx.author.id)
            return await ctx.send("You do not own any items\n")
        if 'bag' not in accounts[str(ctx.author.id)].keys():
            return await ctx.send("You do not own any items\n")
        des = f'**{ctx.author.display_name}\'s Bag**\n\n'
        for thing in accounts[str(ctx.author.id)]['bag']:
            item = Item(dict_form=accounts[str(ctx.author.id)]['bag'][thing])
            des += f"{item.emoji} **{item.name} ─ ** {item.amount}\n*ID* `{item.name}` **─** Sellable\n\n"

        embed = discord.Embed(
            description=des,
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def sell(self, ctx, item, amount=1):
        # await sellItem(ctx, item, amount)
        db = self.cluster['main']
        collection = db['accounts']
        accounts = collection.find_one({'_id': 1})
        if str(ctx.author.id) not in accounts.keys():
            openAccount(ctx.author.id)
            return await ctx.send("You do not own any items.")
        if 'bag' not in accounts[str(ctx.author.id)].keys():
            return await ctx.send("You do no own any items.")
        items = accounts[str(ctx.author.id)]['bag']
        for thing in items:
            temp = Item(dict_form=items[thing])
            if temp.name.lower() == item.lower():
                try:
                    temp.sell(amount)
                except NotEnoughItemsError:
                    return await ctx.send("You do no own enough items.")
                else:
                    return await ctx.send(f"Successfully **sold** `{amount}` {temp.name}")

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
            f'You tried to rob {user.display_name} but there was a massive lock on their door.'
            f' You lost {int(failureProb * 500)} coins',
            f'You tried to rob {user.display_name} but you forgot to carry your tools. '
            f'You lost {int(failureProb * 500)} coins'
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
            if thing.name.lower() == item.lower():
                found = True
                db = self.cluster['main']
                collection = db['accounts']
                accounts = collection.find_one({'_id': 1})
                if str(ctx.author.id) not in accounts.keys():
                    openAccount(ctx.author.id)
                    return await ctx.send("You do not own wny items, Please buy some and try again.")
                if 'bag' not in accounts[str(ctx.author.id)].keys():
                    return await ctx.send("You do not own wny items, Please buy some and try again.")
                if item.lower() not in accounts[str(ctx.author.id)]['bag'].keys():
                    return await ctx.send("You do not own this item, Please buy some and try again.")
                item_model = Item(dict_form=accounts[str(ctx.author.id)]['bag'][item.lower()])
                if item_model.amount < amount:
                    return await ctx.send("You do not own enough of these items, Please buy some more and try again.")
                item_model - amount
                if str(user.id) not in accounts.keys():
                    openAccount(user.id)
                if 'bag' not in accounts[str(user.id)].keys():
                    accounts[str(user.id)]['bag'] = {}
                item_id = random.randint(600000000000000000, 999999999999999999)
                temp_item_model = Item(item_model.name.lower(), item_model.emoji, item_id, amount, item_model.price,
                                       user.id).to_dict()
                accounts[str(user.id)]['bag'][item_model.name.lower()] = temp_item_model
                if item_model.amount == 0:
                    del accounts[str(ctx.author.id)]['bag'][item_model.name.lower()]
                else:
                    accounts[str(ctx.author.id)]['bag'][item_model.name.lower()] = item_model.to_dict()
                collection.update_one({'_id': 1}, {'$set': {str(user.id): accounts[str(user.id)]}})
                collection.update_one({'_id': 1}, {'$set': {str(ctx.author.id): accounts[str(ctx.author.id)]}})
                await ctx.send(f"You **gave** {user.display_name} `{amount}` **{item_model}**")

        if not found:
            await ctx.send("Please specify a valid item")

    @commands.command(aliases=['leaderboard', 'top', 'rich'])
    async def lb(self, ctx, method="wallet"):
        db = self.cluster['main']
        collection = db['accounts']
        accounts = collection.find_one({'_id': 1})
        acc_list = []
        for member in ctx.guild.members:
            if str(member.id) in accounts.keys():
                accounts[str(member.id)]['name'] = member.name
                acc_list.append(accounts[str(member.id)])

        acc_list = custom_sort(acc_list, method)
        des = f'**Richest** users in {ctx.guild.name}\n'
        for i in range(len(acc_list)):
            des += f"{i + 1}. **{acc_list[i]['name']} -** {acc_list[i]['wallet']}\n"

        embed = discord.Embed(
            description=des,
            color=discord.Color.orange()
        )

        await ctx.send(embed=embed)

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
            description=f"To take part in the above heist react below with the :bank: emoji.\n"
                        f"You need at least 2000 coins to participate",
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
    async def bet(self, ctx, amount="", number=0):
        if amount == "":
            return await ctx.send("Please enter a valid amount.")

        if number <= 0:
            return await ctx.send("Please enter a valid number. It should be between 1 and 17.")

        db = self.cluster['main']
        collection = db['accounts']
        accounts = collection.find_one({'_id': 1})
        if str(ctx.author.id) not in accounts.keys():
            openAccount(ctx.author.id)
            return await ctx.send("You currently don't own any casino credits, "
                                  "please buy some using the credit command.")
        if accounts[str(ctx.author.id)]['credits'] == 0:
            return await ctx.send(
                "You currently don't own any casino credits, please buy some using the credit command.")
        creds = 0
        if amount.lower() == "all":
            creds = accounts[str(ctx.author.id)]['credits']
        else:
            try:
                creds = int(amount)
            except ValueError:
                return await ctx.send("Please enter a valid amount")
            else:
                if creds > accounts[str(ctx.author.id)]['credits']:
                    return await ctx.send("You do not have enough credits. Please buy some using the credits command.")

        lucky_number = random.randint(0, 17)
        if lucky_number == number:
            await ctx.send(f"The drawn number is **{lucky_number}**")
            accounts[str(ctx.author.id)]['credits'] += int(0.8 * creds)
            await ctx.send(f"You won **{int(0.8 * creds)}** credits. :partying_face:")
        else:
            await ctx.send(f"The drawn number is **{lucky_number}**")
            accounts[str(ctx.author.id)]['credits'] -= creds
            await ctx.send(f"You lost **{creds}** credits. Better luck next time.")

        collection.update_one({'_id': 1}, {'$set': {str(ctx.author.id): accounts[str(ctx.author.id)]}})

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
            await ctx.send(f"You successfully purchased `{amount}` credits.")
        elif mode.lower() == 'sell':
            await updateBalance(ctx.author.id, amount=int(amount / 3))
            await updateBalance(ctx.author.id, mode="credits", amount=-1 * amount)
            await ctx.send(f"You successfully sold `{amount}` credits.")


def setup(client):
    client.add_cog(Economy(client))
