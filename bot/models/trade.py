from models.item import Item
import discord


class Trade:
    def __init__(self, user: discord.Member):
        self.author = user
        self.items = []
        self.credits = 0
        self.coins = 0
        self.confirmed = False
        self.cfe = '❎'

    def add_items(self, item: Item):
        self.items.append(item)

    def add_credits(self, amount: int):
        self.credits += amount

    def add_coins(self, amount: int):
        self.coins += amount

    def confirm(self):
        self.confirmed = True
        self.cfe = '✅'
