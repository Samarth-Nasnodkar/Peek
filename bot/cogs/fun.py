import discord
from discord.ext import commands
import random


class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def pop(self, ctx, width=3):
        if width > 10:
            return await ctx.send("The size cannot exceed 10")
        elif width <= 1:
            return await ctx.send('The size must be greater than 1')
        element = '||pop||'
        content = (element*width + '\n')*width
        await ctx.send(content)

    @commands.command()
    async def choose(self, ctx, *options):
        options = list(options)
        run = True
        i = 0
        while run:
            try:
                if options[i] == ',':
                    options.pop(i)
                    i -= 1
                elif options[i].endswith(','):
                    options[i] = options[i][:-1]
                elif options[i].startswith(','):
                    options[i] = options[i][1:]
            except IndexError:
                run = not run
            else:
                i += 1

        random_choice = random.choice(options)
        await ctx.send(f"**{random_choice}**")


def setup(client):
    client.add_cog(Fun(client))
