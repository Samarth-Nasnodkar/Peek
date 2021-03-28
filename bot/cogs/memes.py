import discord
from discord.ext import commands, tasks
from database.imgs import imgs
import asyncpraw
import random
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import json
import pymongo
from pymongo import MongoClient


class Memes(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.cluster = MongoClient(
            "mongodb+srv://dbBot:samarth1709@cluster0.moyjp.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
        self.subreddits = ['dankmemes', 'memes', 'PrequelMemes', 'pcmasterrace', 'PewdiepieSubmissions']
        self.reddit = asyncpraw.Reddit(client_id='0bD1UHrRzjDbGQ',
                                       client_secret='9xoApJv0eZeRr1QVGJJulIE5cjXyFg',
                                       username='CooLDuDE-6_9',
                                       password='samarth1709',
                                       user_agent='AmongUsUnofficial')
        self.updateMeme.start()

    @tasks.loop(minutes=30)
    async def updateMeme(self):
        await self.client.wait_until_ready()
        print("Attempting to log memes")
        memeList = {}

        for subreddit in self.subreddits:
            memes = await self.reddit.subreddit(subreddit)
            hot = memes.top("day", limit=20)
            async for meme in hot:
                memeList[meme.title] = {}
                memeList[meme.title]["score"] = meme.score
                memeList[meme.title]["url"] = meme.url
                memeList[meme.title]["comments"] = len(await meme.comments())

        db = self.cluster['main']
        collection = db['memes']
        collection.update_one({'_id': 2}, {'$set': {'memes': memeList}})
        print("Logged Memes")

    @commands.command()
    async def meme(self, ctx):
        db = self.cluster['main']
        collection = db['memes']
        loggedMemes = collection.find_one({'_id': 2})['memes']
        if loggedMemes is None:
            memeList = {}
            for subreddit in self.subreddits:
                memes = await self.reddit.subreddit(subreddit)
                hot = memes.top("day", limit=20)
                async for meme in hot:
                    memeList[meme.title] = {}
                    memeList[meme.title]["score"] = meme.score
                    memeList[meme.title]["url"] = meme.url
                    memeList[meme.title]["comments"] = len(await meme.comments())

            sendable_meme = random.choice(memeList)
            embed = discord.Embed(
                description=f'***__[{memeList[sendable_meme].title}]({memeList[sendable_meme].url})__***',
                color=discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
            embed.set_image(url=memeList[sendable_meme].url)
            embed.set_footer(text=f'🔥 {memeList[sendable_meme].score}')
            await ctx.send(embed=embed)
        else:
            memeList = loggedMemes
            sendable_meme = random.choice(list(memeList))
            embed = discord.Embed(description=f"***__[{sendable_meme}]({memeList[sendable_meme]['url']})__***",
                                  color=discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255),
                                                               random.randint(0, 255)))
            embed.set_image(url=memeList[sendable_meme]["url"])
            embed.set_footer(text=f"🔥 {memeList[sendable_meme]['score']} | 💬 {memeList[sendable_meme]['comments']}")
            await ctx.send(embed=embed)

    @commands.command()
    async def google(self, ctx, text=None):
        await ctx.send(file=discord.File(imgs['google']))

    @commands.command(aliases=['electroboom'])
    async def electro(self, ctx, *, text=''):
        if text == '':
            return await ctx.send('You need to pass some text.')

        if len(text) > 130:
            return await ctx.send('Your text cannot exceed 130 characters.')

        img = Image.open(imgs['electro'])
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype('database/fonts/arial.ttf', 80)

        increment = 0
        if len(text) > 26:
            txt = ''

            while len(text) > 26:
                txt = text[0:25]
                draw.text((800, 130 + increment), txt, (0, 0, 0), font=font)
                increment += 170
                text = text[25:]

            draw.text((800, 130 + increment), text, (0, 0, 0), font=font)

        else:
            draw.text((800, 130), text, (0, 0, 0), font=font)

        img.save('database/images/electroout.png')
        await ctx.send(file=discord.File('database/images/electroout.png'))

    @commands.command()
    async def unplug(self, ctx, *, text=''):
        if text == '':
            return await ctx.send('You need to pass some text.')

        if len(text) > 60:
            return await ctx.send('Your text cannot exceed 60 characters.')

        img = Image.open(imgs['unplug'])
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype('database/fonts/arial.ttf', 15)
        increment = 0
        if len(text) > 30:
            txt = ''
            while len(text) > 30:
                txt = text[0:29]
                draw.text((375, 30 + increment), txt, (0, 0, 0), font=font)
                increment += 30
                text = text[29:]

            draw.text((375, 30 + increment), text, (0, 0, 0), font=font)
        else:
            draw.text((375, 30), text, (0, 0, 0), font=font)

        img.save('database/images/unplugout.jpg')
        await ctx.send(file=discord.File('database/images/unplugout.jpg'))

    @commands.command()
    async def boo(self, ctx, *, text=''):
        if text == '':
            return await ctx.send('You need to pass some text.')

        if len(text) > 32:
            return await ctx.send('your text cannot exceed 32 characters.')

        img = Image.open(imgs['boo'])
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype('database/fonts/arial.ttf', 30)
        increment = 0
        if len(text) > 16:
            while len(text) > 16:
                txt = ''
                txt = text[0:15]
                draw.text((553, 660 + increment), txt, (0, 0, 0), font=font)
                increment += 50
                text = text[15:]

            draw.text((553, 660 + increment), text, (0, 0, 0), font=font)
        else:
            draw.text((553, 660), text, (0, 0, 0), font=font)

        img.save('database/images/booout.png')
        await ctx.send(file=discord.File('database/images/booout.png'))

    @commands.command()
    async def fact(self, ctx, *, text=''):
        if text == '':
            return await ctx.send('You need to pass some text.')

        if len(text) > 78:
            return await ctx.send('Your text cannot exceed 78 characters.')

        img = Image.open(imgs['fact'])
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype('database/fonts/arial.ttf', 30)
        increment = 0
        if len(text) > 26:
            txt = ''
            while len(text) > 26:
                txt = text[0:25]
                draw.text((50, 690 + increment), txt, (0, 0, 0), font=font)
                text = text[25:]
                increment += 40

            draw.text((50, 690 + increment), text, (0, 0, 0), font=font)
        else:
            draw.text((50, 690), text, (0, 0, 0), font=font)

        img.save('database/images/factout.jpg')
        await ctx.send(file=discord.File('database/images/factout.jpg'))

    @commands.command()
    async def bastards(self, ctx, *, text=''):
        if text == '':
            return await ctx.send('You need to pass some text.')

        if len(text) > 78:
            return await ctx.send('Your text cannot exceed 78 characters.')

        img = Image.open(imgs['bastards'])
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype('database/fonts/arial.ttf', 60)

        increment = 0
        if len(text) > 26:
            txt = ''
            while len(text) > 26:
                txt = text[0:25]
                draw.text((17, 17 + increment), txt, (0, 0, 0), font=font)
                increment += 70
                text = text[25:]

            draw.text((17, 17 + increment), text, (0, 0, 0), font=font)

        else:
            draw.text((17, 17), text, (0, 0, 0), font=font)

        img.save('database/images/bastardsout.jpg')
        await ctx.send(file=discord.File('database/images/bastardsout.jpg'))

    @commands.command()
    async def monster(self, ctx, *, text=''):
        if text == '':
            return await ctx.send('You need to pass some text.')

        if len(text) > 60:
            return await ctx.send('Your text cannot exceed 60 characters')
        img = Image.open(imgs['monster'])
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype('database/fonts/arial.ttf', 20)
        increment = 0
        if len(text) > 30:
            txt = ''
            while len(text) > 30:
                txt = text[0:29]
                draw.text((45, 370 + increment), txt, (0, 0, 0), font=font)
                increment += 40
                text = text[29:]

            draw.text((45, 370 + increment), text, (0, 0, 0), font=font)
        else:
            draw.text((45, 370), text, (0, 0, 0), font=font)

        img.save('database/images/monsterout.jpg')
        await ctx.send(file=discord.File('database/images/monsterout.jpg'))

    @commands.command()
    async def drake(self, ctx, *, text=''):
        if text == '':
            return await ctx.send('You need to pass some text separated by a ","')

        index = text.find(',')
        if index == -1:
            return await ctx.send('You need to pass some text separated by a ","')

        text_one, text_two = text.split(',')

        if len(text_one) > 42 or len(text_two) > 42:
            return await ctx.send('Your text cannot exceed 48 characters(total of 84 including both).')

        img = Image.open(imgs['drake'])
        draw = ImageDraw.Draw(img)
        t_one = text_one
        t_two = text_two
        font = ImageFont.truetype('database/fonts/arial.ttf', 60)
        increment = 0
        if len(t_one) > 14:
            while len(text_one) > 14:
                t_one = text_one[0:13]
                draw.text((520, 40 + increment), t_one, (0, 0, 0), font=font)
                increment += 130
                text_one = text_one[13:]

            draw.text((520, 40 + increment), text_one, (0, 0, 0), font=font)
        else:
            draw.text((520, 40), t_one, (0, 0, 0), font=font)

        increment = 0
        if len(text_two) > 14:
            while len(text_two) > 14:
                t_two = text_two[0:13]
                draw.text((520, 460 + increment), t_two, (0, 0, 0), font=font)
                increment += 130
                text_two = text_two[13:]

            draw.text((520, 460 + increment), text_two, (0, 0, 0), font=font)
        else:
            draw.text((520, 460), t_two, (0, 0, 0), font=font)

        img.save('database/images/drakeout.jpg')
        await ctx.send(file=discord.File('database/images/drakeout.jpg'))

    @commands.command()
    async def sword(self, ctx, *, text=''):
        if text == '':
            return await ctx.send('You have to provide two texts separated by a ","')

        index = text.find(',')

        if index == -1:
            return await ctx.send('You have to provide two texts separated by a ","')

        # 132,73 font = 40

        # 11 , 12

        text_one, text_two = text.split(',')
        if len(text_one) > 10 or len(text_two) > 20:
            return await ctx.send('The first text should not exceed 11 characters and second cannot exceed 21.')

        img = Image.open(imgs['sword'])
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype('database/fonts/arial.ttf', 40)
        draw.text((132, 73), text_one, (0, 0, 0), font=font)
        draw.text((68, 273), text_two, (0, 0, 0), font=font)

        img.save('database/images/swordout.jpg')
        await ctx.send(file=discord.File('database/images/swordout.jpg'))

    @commands.command()
    async def announce(self, ctx, *, text=''):
        if text == '':
            return await ctx.send('You need to pass some text.')

        if len(text) > 78:
            return await ctx.send('Your text cannot exceed 78 characters.')

        font = ImageFont.truetype('database/fonts/arial.ttf', 60)
        img = Image.open(imgs['announce'])
        draw = ImageDraw.Draw(img)
        increment = 0
        if len(text) > 26:
            txt = ''
            while len(text) > 26:
                txt = text[0:25]
                draw.text((450, 80 + increment), txt, (0, 0, 0), font=font)
                increment += 145
                text = text[25:]

            draw.text((450, 80 + increment), text, (0, 0, 0), font=font)
        else:
            draw.text((450, 80), text, (0, 0, 0), font=font)

        img.save('database/images/announceout.png')
        await ctx.send(file=discord.File('database/images/announceout.png'))

    @commands.command()
    async def fbi(self, ctx, *, text=''):
        if text == '':
            return await ctx.send('You need to provide some text.')

        if len(text) > 32:
            return await ctx.send('Your text cannot exceed 32 characters.')

        img = Image.open(imgs['fbi'])
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype('database/fonts/arial.ttf', 60)

        draw.text((45, 450), text, (0, 0, 0), font=font)

        img.save('database/images/fbiout.jpg')
        await ctx.send(file=discord.File('database/images/fbiout.jpg'))

    @commands.command()
    async def worthless(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author

        bg = Image.open(imgs['worthless'])
        asset = user.avatar_url_as(format='jpg', size=128)
        data = BytesIO(await asset.read())
        pfp = Image.open(data)
        pfp = pfp.resize((231, 231))
        bg.paste(pfp, (304, 166))
        bg.save('database/images/worthlessout.jpg')
        await ctx.send(file=discord.File('database/images/worthlessout.jpg'))

    @commands.command()
    async def smile(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author

        bg = Image.open(imgs['smile'])
        asset = user.avatar_url_as(format='jpg', size=128)
        data = BytesIO(await asset.read())
        pfp = Image.open(data)
        pfp = pfp.resize((120, 120))
        bg.paste(pfp, (150, 20))
        bg.save('database/images/smileout.jpg')
        await ctx.send(file=discord.File('database/images/smileout.jpg'))

    @commands.command()
    async def slap(self, ctx, user: discord.Member = None):
        if user is None:
            return await ctx.send('You need to mention someone to use this command.')

        if user == ctx.author:
            return await ctx.send('You cannot slap yourself. Please mention someone else.')

        bg = Image.open(imgs['slap'])
        authorAsset = ctx.author.avatar_url_as(format='jpg', size=128)
        userAsset = user.avatar_url_as(format='jpg', size=128)

        authorData = BytesIO(await authorAsset.read())
        userData = BytesIO(await userAsset.read())
        authorPFP = Image.open(authorData)  # 298
        userPFP = Image.open(userData)  # 338
        authorPFP = authorPFP.resize((298, 298))
        userPFP = userPFP.resize((338, 338))
        bg.paste(authorPFP, (479, 94))
        bg.paste(userPFP, (815, 334))

        bg.save('database/images/slapout.jpg')
        await ctx.send(file=discord.File('database/images/slapout.jpg'))

    @commands.command(aliases=['armour'])
    async def armor(self, ctx, *, text=''):
        if text == '':
            return await ctx.send('You need to pass some text.')

        if len(text) > 60:
            return await ctx.send('your text cannot exceed 60 characters')

        img = Image.open(imgs['armor'])
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype('database/fonts/arial.ttf', size=20)
        increment = 0
        if len(text) > 20:
            txt = ''
            while len(text) > 20:
                txt = text[0:19]
                draw.text((40, 370 + increment), txt, (0, 0, 0), font=font)
                text = text[19:]
                increment += 40

            draw.text((40, 370 + increment), text, (0, 0, 0), font=font)
        else:
            draw.text((40, 370), text, (0, 0, 0), font=font)

        img.save('database/images/armorout.png')
        await ctx.send(file=discord.File('database/images/armorout.png'))

    @commands.command()
    async def patrick(self, ctx, *, text=''):
        if text == '':
            return await ctx.send('You need to pass some text.')

        img = Image.open(imgs['patrick'])
        font = ImageFont.truetype('database/fonts/arial.ttf', 40)
        draw = ImageDraw.Draw(img)

        if len(text) > 33:
            return await ctx.send('Your text cannot excceed 33 characters.')

        increment = 0
        if len(text) > 11:
            txt = ''
            while len(text) > 11:
                txt = text[0:10]
                draw.text((130, 470 + increment), txt, (0, 0, 0), font=font)
                increment += 70
                text = text[10:]

            draw.text((130, 470 + increment), text, (0, 0, 0), font=font)

        else:
            draw.text((130, 470), text, (0, 0, 0), font=font)

        img.save('database/images/patrickout.jpg')
        await ctx.send(file=discord.File('database/images/patrickout.jpg'))

    @commands.command()
    async def prison(self, ctx, *, text=''):
        if text == '':
            return await ctx.send('You need to pass some text.')

        if len(text) > 52:
            return await ctx.send('Your text cannot exceed 52 characters.')

        img = Image.open(imgs['prison'])
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype('database/fonts/arial.ttf', 20)
        increment = 0

        if len(text) > 26:
            txt = ''
            while len(text) > 26:
                txt = text[0:25]
                draw.text((35, 395 + increment), txt, (0, 0, 0), font=font)
                increment += 30
                text = text[25:]

            draw.text((35, 395 + increment), text, (0, 0, 0), font=font)
        else:
            draw.text((35, 395), text, (0, 0, 0), font=font)

        img.save('database/images/prisonout.png')
        await ctx.send(file=discord.File('database/images/prisonout.png'))

    @commands.command()
    async def spongebob(self, ctx, *, text=''):
        if text == '':
            return await ctx.send('You need to pass some text.')

        img = Image.open(imgs['spongebob'])
        font = ImageFont.truetype('database/fonts/arial.ttf', 30)
        draw = ImageDraw.Draw(img)

        if len(text) > 44:
            return await ctx.send('Your text cannot excceed 44 characters.')

        increment = 0
        if len(text) > 11:
            txt = ''
            while len(text) > 11:
                txt = text[0:10]
                draw.text((60, 85 + increment), txt, (0, 0, 0), font=font)
                increment += 40
                text = text[10:]

            draw.text((60, 85 + increment), text, (0, 0, 0), font=font)

        else:
            draw.text((60, 85), text, (0, 0, 0), font=font)

        img.save('database/images/spongeout.png')
        await ctx.send(file=discord.File('database/images/spongeout.png'))

    @commands.command()
    async def shit(self, ctx, *, text=''):
        if text == '':
            return await ctx.send('You need to pass some text.')

        img = Image.open(imgs['shit'])
        font = ImageFont.truetype('database/fonts/arial.ttf', 15)
        draw = ImageDraw.Draw(img)

        if len(text) > 33:
            return await ctx.send('Your text cannot excceed 33 characters.')

        increment = 0
        if len(text) > 11:
            txt = ''
            while len(text) > 11:
                txt = text[0:10]
                draw.text((90, 210 + increment), txt, (0, 0, 0), font=font)
                increment += 30
                text = text[10:]

            draw.text((90, 210 + increment), text, (0, 0, 0), font=font)

        else:
            draw.text((90, 210), text, (0, 0, 0), font=font)

        img.save('database/images/shitout.jpg')
        await ctx.send(file=discord.File('database/images/shitout.jpg'))

    @commands.command()
    async def santa(self, ctx, *, text=''):
        if text == '':
            return await ctx.send('You need to pass some text.')

        img = Image.open(imgs['santa'])
        font = ImageFont.truetype('database/fonts/arial.ttf', 30)
        draw = ImageDraw.Draw(img)

        if len(text) > 72:
            return await ctx.send('Your text cannot excceed 72 characters.')

        increment = 0
        if len(text) > 18:
            txt = ''
            while len(text) > 18:
                txt = text[0:17]
                draw.text((40, 475 + increment), txt, (0, 0, 0), font=font)
                increment += 40
                text = text[17:]

            draw.text((40, 475 + increment), text, (0, 0, 0), font=font)

        else:
            draw.text((40, 475), text, (0, 0, 0), font=font)

        img.save('database/images/santaout.jpg')
        await ctx.send(file=discord.File('database/images/santaout.jpg'))


def setup(client):
    client.add_cog(Memes(client))
