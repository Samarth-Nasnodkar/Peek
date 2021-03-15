import discord
from discord.ext import menus
from database.cmds import get_emb


class Help(menus.Menu):
    def __init__(self, prefix):
        self.Embeds = get_emb(prefix)
        super().__init__(timeout=30.0, clear_reactions_after=True)

    async def send_initial_message(self, ctx, channel):
        embed = discord.Embed(
            title=f"Bot Help!",
            description=f"Welcome to Bot help\n\n```🎲 ➜ Economy help\n📋 ➜ Moderation help\n🏆 ➜ Memes help\n```"
        )
        embed.set_thumbnail(url="https://i.imgur.com/x2zK2Fp.gif")
        return await channel.send(embed=embed)

    @menus.button("🎲")
    async def eco(self, payload):
        self.Embeds[0].set_footer(text=f"Command ran by {self.ctx.author}")
        await self.message.edit(embed=self.Embeds[0])

    @menus.button("📋")
    async def mod(self, payload):
        self.Embeds[1].set_footer(text=f"Command ran by {self.ctx.author}")
        await self.message.edit(embed=self.Embeds[1])

    @menus.button("🏆")
    async def meme(self, payload):
        self.Embeds[2].set_footer(text=f"Command ran by {self.ctx.author}")
        await self.message.edit(embed=self.Embeds[2])
