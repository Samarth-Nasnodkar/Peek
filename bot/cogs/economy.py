import discord
from discord.ext import commands
from cogs.helpers import *
from datetime import datetime
import random
from database.mainshop import shop
import asyncio
import time


class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['balance'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def bal(self, ctx, user: discord.Member = None):
        if user is None: user = ctx.author

        bal = balance(user.id)
        embed = discord.Embed(
            title=f"{user.display_name}'s Balance",
            description=f":dollar:**Wallet** : `{bal['wallet']}` coins\n:bank:**Bank** : `{bal['bank']}` coins\n\n",
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

        def check(reaction: discord.Reaction, person):
            return str(reaction.emoji) == '🏦' and reaction.message.channel == ctx.channel

        emb = await ctx.send(embed=heistEmbed)
        await emb.add_reaction('🏦')
        start = time.time()
        proceed = False
        run = True
        while run:
            try:
                reaction, person = await self.client.wait_for('reaction_add', timeout=0.5, check=check)
                print(f'{person} just reacted')
                if person.id != 819946835485261825:
                    heisters.append(person)
            except asyncio.TimeoutError:
                if len(heisters) > 0:
                    proceed = True
            finally:
                if int(time.time() - start) >= 10 and proceed:
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
                else:
                    run = True


def setup(client):
    client.add_cog(Economy(client))
