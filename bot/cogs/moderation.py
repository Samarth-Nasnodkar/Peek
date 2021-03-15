import discord
from discord.ext import commands
import asyncio
from cogs.helpers import toTime, timeConvertible
from cogs.help import Help
from bot import update_prefix, get_prefix


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.icon = "https://i.imgur.com/x2zK2Fp.gif"

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
            if not duration is None:
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
