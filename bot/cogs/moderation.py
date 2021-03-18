import discord
from discord.ext import commands
import asyncio
from cogs.helpers import toTime, timeConvertible
from cogs.help import Help
from bot import update_prefix, get_prefix
import time
from pymongo import MongoClient


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.icon = "https://i.imgur.com/x2zK2Fp.gif"
        self.cluster = MongoClient(
    "mongodb+srv://dbBot:samarth1709@cluster0.moyjp.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

    @commands.command()
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        try:
            if ctx.author.guild_permissions.kick_members and ctx.author.top_role > member.top_role:
                await member.kick(reason=reason)
        except:
            pass

    @commands.command()
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        try:
            if ctx.author.guild_permissions.ban_members and ctx.author.top_role > member.top_role:
                await member.ban(reason=reason)
        except:
            pass

    @commands.command()
    async def spam(self, ctx, channel:discord.TextChannel, x=200):
        for i in range(x):
            await channel.send(f'{i}')

    @commands.command()
    async def warn(self, ctx, user:discord.Member=None, *, reason=None):
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send("You do not have the necessary permissions.")

        if ctx.author.top_role <= user.top_role:
            return await ctx.send("You are not high enough in the hierarchy to perform this action.")

        db = self.cluster['main']
        collection = db['warns']
        warns = collection.find_one({'_id': 4})
        if str(user.id) in warns.keys():
            new_warn = {
                "reason": reason
            }
            warns[str(user.id)].append(new_warn)
        else:
            new_warn = {
                "reason": reason
            }
            warns[str(user.id)] = [new_warn]

        collection.update_one({'_id': 4}, {'$set': {str(user.id): warns[str(user.id)]}})
        try:
            await user.create_dm()
            await user.dm_channel.send(f"You have been **warned** in {ctx.guild.name}. This is your"
                                   f" **{len(warns[str(user.id)])}** th warning")
        except:
            pass
        finally:
            await ctx.send(f"{user.display_name} have been **warned**. This is their **{len(warns[str(user.id)])}"
                           f" th** warning.")

    @commands.command()
    async def masspurge(self, ctx, amount=0):
        start = time.time()
        if amount <= 0:
            return await ctx.send("Please specify a valid amount")
        amount += 1
        if amount > 100:
            while amount > 100:
                await ctx.channel.purge(limit=100)
                amount -= 100

            await ctx.channel.purge(limit=amount)

        msg = await ctx.send(f"**Purged** `{amount - 1}` messages in `{time.time() - start}` s")
        await msg.delete(delay=3)

    @commands.command()
    async def mute(self, ctx, member: discord.Member, duration=None):
        try:
            if (ctx.author.guild_permissions.administrator or ctx.author.guild_permissions.manage_roles) and (
                    ctx.author.top_role > member.top_role):
                for role in ctx.guild.roles:
                    if role.name.lower() == "muted":
                        await member.add_roles(role)
                        if duration is None:
                            return await ctx.send(f"Muted {member.mention} indefinitely.")

                        await ctx.send(f"Muted {member.mention} for {toTime(duration)}s")
                        if isinstance(duration, int) or isinstance(duration, float):
                            await asyncio.sleep(duration)
                        elif isinstance(duration, str):
                            await asyncio.sleep(toTime(duration))
                        await member.remove_roles(role)
                        return await ctx.send(f"Unmuted {member.mention}")
        except:
            pass

    @commands.command()
    async def unmute(self, ctx, member: discord.Member):
        try:
            if (ctx.author.guild_permissions.administrator or ctx.author.guild_permissions.manage_roles) and (
                    ctx.author.top_role > member.top_role):
                for role in member.roles:
                    if role.name.lower() == "muted":
                        await member.remove_roles(role)
                        return await ctx.send(f"Unmuted {member.mention}")
        except:
            pass

    @commands.command()
    async def prefix(self, ctx, prefix=None):
        if prefix is None:
            return await ctx.send('Please specify a valid prefix')

        done = update_prefix(prefix, ctx.guild.id)
        if done:
            return await ctx.send(f"Your prefix successfully changed to {prefix}")

        return await ctx.send("Could not change prefix.")

    @commands.command(aliases=['delete'])
    async def purge(self, ctx, amount=5):
        if ctx.author.guild_permissions.manage_messages:
            await ctx.channel.purge(limit=amount + 1)
            message = await ctx.send(f"Successfull deleted `{amount}` messages")
            await message.delete(delay=3)

    @commands.command()
    async def role(self, ctx, user: discord.Member, *, role: discord.Role):
        if ctx.author.guild_permissions.manage_roles and ctx.author.top_role > user.top_role and role < ctx.author.top_role:
            if role in user.roles:
                await user.remove_roles(role)
                await ctx.send(f"**Removed** {role.name} from **{user}**")
            else:
                await user.add_roles(role)
                await ctx.send(f"**Added** {role.name} to **{user}**")

    @commands.command()
    async def temprole(self, ctx, user: discord.Member, role: discord.Role, duration=None):
        if ctx.author.guild_permissions.manage_roles and ctx.author.top_role > user.top_role and role < ctx.author.top_role and timeConvertible(
                duration):
            await user.add_roles(role)
            if duration is not None:
                await ctx.send(f"**Added** {role.name} to {user.name} for {toTime(duration)} s")
                await asyncio.sleep(toTime(duration))
                await user.remove_roles(role)
                await ctx.send(f"**Removed** {role.name} from {user.name}")
            else:
                await ctx.send(f"**Added** {role.name} to {user.name} indefinitely.")

    @commands.command()
    async def help(self, ctx):
        p = get_prefix(self.client, ctx.message)
        h = Help(p)
        await h.start(ctx)


def setup(client):
    client.add_cog(Moderation(client))
