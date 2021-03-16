import discord
from discord.ext import commands

eco = [
    {
        "name": "balance",
        "description": "Shows your balance"
    },
    {
        "name": "beg",
        "description": "Gives you some random money"
    },
    {
        "name": "shop",
        "description": "Shows all the available items in the shop"
    },
    {
        "name": "buy <item> <amount(default = 1)>",
        "description": "Lets you buy that item"
    },
    {
        "name": "bag",
        "description": "Shows you all the items you own"
    },
    {
        'name': 'sell <item> <amount(default = 1)>',
        'description': "Sells the items and returns you 60% price."
    },
    {
        'name': 'rob <user>',
        'description': 'Wanna be richer? try robbing a few people.'
    },
    {
        'name': 'give <user> <amount>',
        'description': 'transfers the specified amount of money from your account to the user\'s account'
    },
    {
        'name': 'heist <user>',
        'description': 'plans a group heist against the user. The reward is equally split among all heisters'
    },
    {
        'name': 'credits <(buy/sell)> <amount>',
        'description': 'lets you buy/sell the specified amount of credits. 1 coin = 3 credits'
    },
    {
        'name': 'slots <amount>',
        'description': 'lets you bet those credits. This can have some high returns'
    }
]

mod = [
    {
        "name": "kick <user> <reason>",
        "description": "Kicks the mentioned user from the server"
    },
    {
        "name": "ban <user> <reason>",
        "description": "Bans the mentioned user from the server"
    },
    {
        "name": "mute <user> <duration>",
        "description": "Mutes the user for the specified time.\nTime of format m/hr/s"
    },
    {
        "name": "unmute <user>",
        "description": "Unmuted the mentnioned user"
    },
    {
        "name": "purge <amount>",
        "description": "Deletes the specified number of messages"
    }
]

memes = [
    {
        "name": "meme",
        "description": "Grabs a random meme from Reddit"
    },
    {
        "name": "google",
        "description": "Generates a Google is down meme"
    },
    {
        "name": "electro <text>",
        "description": "Generates a change my mind meme"
    },
    {
        "name": "unplug <text>",
        "description": "Never say that."
    },
    {
        "name": "boo",
        "description": "Generates a ghost booing meme"
    },
    {
        "name": "fact <text>",
        "description": "Whoa, Noish facts!"
    },
    {
        "name": "bastards <text>",
        "description": "Those bastards lied to me"
    },
    {
        "name": "monster <text>",
        "description": "He is sCaRy"
    },
    {
        "name": "drake <text> , <text>",
        "description": "Generates a drake meme"
    },
    {
        "name": "sword <text> <text>",
        "description": "Sword big but bRoKeN"
    },
    {
        "name": "announce <text>",
        "description": "Announce it in the Simpson style!"
    },
    {
        "name": "fbi <text>",
        "description": "Why is the FBI here?"
    },
    {
        "name": "worthless <user(optional)>",
        "description": "That user is completely useless. F."
    },
    {
        "name": "smile <user(optional)>",
        "description": "That damn smile .."
    },
    {
        "name": "slap <user>",
        "description": "They deserver a SLAP."
    },
    {
        "name": "armor <text>",
        "description": "Nothing can panetrate this armor"
    },
    {
        "name": "patrick <text>",
        "description": "That was scary!!"
    },
    {
        "name": "prison <text>",
        "description": "So , What was your crime?"
    },
    {
        "name": "spongebob <text>",
        "description": "Just burn it. burn it ..."
    },
    {
        "name": "shit <text>",
        "description": "This is just pure shit."
    },
    {
        "name": "santa <text>",
        "description": "Ooh, Santa angry!!"
    }
]

cmdList = [eco, mod, memes]


# def fetch_prefix(server_id):
#     db = cluster["main"]
#     collection = db["entry"]  
#     prefixes = collection.find_one({"_id" : 0})
#     if prefixes is None: return "$"
#     elif str(server_id) in prefixes.keys() : return prefixes[str(server_id)]
#     return "$"

def getDesc(ind, prefix):
    f = cmdList[ind]
    desc = "```css\n"
    for cmd in f:
        desc += f"[{prefix}{cmd['name']}] ➜ {cmd['description']}\n"

    desc += "```"
    return desc


def get_emb(prefix):
    EcoEmbed = discord.Embed(
        title=f"🎲 Economy",
        description=getDesc(0, prefix),
        color=discord.Color.orange()
    )
    ModEmbed = discord.Embed(
        title=f"📋 Moderation",
        description=getDesc(1, prefix),
        color=discord.Color.orange()
    )
    MemeEmbed = discord.Embed(
        title=f"🏆 Memes",
        description=getDesc(2, prefix),
        color=discord.Color.orange()
    )
    EcoEmbed.set_thumbnail(url="https://i.imgur.com/x2zK2Fp.gif")
    ModEmbed.set_thumbnail(url="https://i.imgur.com/x2zK2Fp.gif")
    MemeEmbed.set_thumbnail(url="https://i.imgur.com/x2zK2Fp.gif")
    Embeds = [
        EcoEmbed,
        ModEmbed,
        MemeEmbed
    ]
    return Embeds
