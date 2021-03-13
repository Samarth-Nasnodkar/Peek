import discord
from discord.ext import commands
from cogs.helpers import *
from datetime import datetime
import random
from database.mainshop import shop

class Economy(commands.Cog):
    def __init__(self , client):
        self.client = client

    @commands.command(aliases = ['bal'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def balance(self , ctx , user : discord.Member = None):
        if user is None : user = ctx.author

        bal = balance(user.id)
        embed = discord.Embed(
            title = f"{user.display_name}'s Balance",
            description = f":dollar:**Wallet** : `{bal['wallet']}` coins\n:bank:**Bank** : `{bal['bank']}` coins\n\n",
            color = discord.Color.orange()
        )
        embed.set_footer(text = f"Command ran by {ctx.author.display_name}")
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed = embed)

    @balance.error
    async def bal_error(self , ctx , error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = 'Command on cooldown for {:.2f}s'.format(error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def beg(self , ctx):
        earned = random.randint(50 , 600)
        if await updateBalance(ctx.author.id , "wallet" , amount = earned):
            await ctx.send(f"You earned {earned} coins")

    @beg.error
    async def beg_error(self , ctx , error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = 'Command on cooldown for {:.2f}s'.format(error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    @commands.command()
    async def shop(self , ctx):
        description = ""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        for item in shop:
            description += f"{item['emoji']}**{item['name']}** - [⏣ {item['price']}]({url})\n"

        embed = discord.Embed(
            title = "*__Shop Items__*",
            description = description,
            color = discord.Color.orange()
        )

        await ctx.send(embed = embed)

    @commands.command()
    async def buy(self , ctx , item , amount = 1):
        transaction = await purchase(ctx.author.id , item , amount)
        if transaction : return await ctx.send(f"Successfully purchased `{amount}` {item.lower()}")
        return await ctx.send('Purchase failed.')

    @commands.command(aliases = ['inv' , 'inventory'])
    async def bag(self , ctx):
        await showBagitems(ctx)

    @commands.command()
    async def sell(self , ctx , item , amount = 1):
        await sellItem(ctx , item , amount)

    @commands.command(aliases = ['deposit'])
    async def dep(self , ctx , amount = ""):
        if amount == "": return await ctx.send("Please specify an amount")
        db = cluster['main']
        collection = db['accounts']
        accounts = collection.find_one({'_id' : 1})
        if amount.lower() == "all":
            await updateBalance(ctx.author.id , amount=-1*accounts[str(ctx.author.id)]['wallet'])
            await updateBalance(ctx.author.id , "bank" , amount=accounts[str(ctx.author.id)]['wallet'])
            return await ctx.send(f"Successfully deposited `{accounts[str(ctx.author.id)]['wallet']}` coins")
        else:
            try:
                amt = int(amount)
                if amt > accounts[str(ctx.author.id)]['wallet']:
                    return await ctx.send("You do not have enough coins")

                await updateBalance(ctx.author.id , amount = -1*amt)
                await updateBalance(ctx.author.id , "bank",amount = 1*amt)
                await ctx.send(f"Successfully deposited `{amt}` coins")
            except ValueError:
                return await ctx.send(f"Please specify a valid amount.")

    @commands.command(aliases = ['with'])
    async def withdraw(self , ctx , amount = ""):
        if amount == "": return await ctx.send("Please specify an amount")
        db = cluster['main']
        collection = db['accounts']
        accounts = collection.find_one({'_id' : 1})
        if amount.lower() == "all":
            await updateBalance(ctx.author.id , amount=accounts[str(ctx.author.id)]['bank'])
            await updateBalance(ctx.author.id , "bank" , amount=-1*accounts[str(ctx.author.id)]['bank'])
            return await ctx.send(f"Successfully withdrew `{accounts[str(ctx.author.id)]['bank']}` coins")
        else:
            try:
                amt = int(amount)
                if amt > accounts[str(ctx.author.id)]['bank']:
                    return await ctx.send("You do not have enough coins")

                await updateBalance(ctx.author.id , amount = amt)
                await updateBalance(ctx.author.id , "bank" , amount = -1*amt)
                await ctx.send(f"Successfully withdrew `{amt}` coins")
            except ValueError:
                return await ctx.send(f"Please specify a valid amount.")


def setup(client):
    client.add_cog(Economy(client))