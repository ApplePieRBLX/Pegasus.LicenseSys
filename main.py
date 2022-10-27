from discord.ext import commands
import random
import string
from datetime import datetime
from datetime import timedelta
import datetime
import discord
from pymongo import MongoClient


bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())

#all your mongo db information
mongo_db_link = 'Put your mongo db connection string'
databases_name = 'Put your database name here' # -- Example https://ibb.co/1fpQktR
collection_name = "Put your database collection name here" # -- Example https://ibb.co/Fwwvbxw

#key information
role_name = "Customer"
key_prefix = "Peg" # -- Example: Discord-qpPYfnDZhiahUFWzSPkQsLXxt

@bot.command()
@commands.has_permissions(manage_roles=True)  
async def gen(ctx, amount, time):
   key_int = int(amount)
   amount = key_int
   key_amt = range(int(amount))
   time = int(time)

   # -- Connect to database n shit
   mongo_url = mongo_db_link
   cluster = MongoClient(mongo_url)
   db = cluster[f"{databases_name}"]
   collection = db[f"{collection_name}"]

   # -- Expiration
   now = datetime.datetime.today()
   future = now + timedelta(days=time)
   expires = future.strftime("%y-%m-%d")

   # -- Key
   key_yes = f"{key_prefix}-cIrbacRELqJSLEObRVkqEGVZi"
   if key_int == 1:
      letters = string.ascii_letters
      key = f"{key_prefix}-" + ''.join(random.choice(letters) for i in range(25))
   elif key_int < 1:
      em = discord.Embed(color=0xff0000)
      em.add_field(name="Invalid number", value="Key amount needs to be higher than 0")
      await ctx.send(embed=em)
      return 0
   elif key_int > 1:
      amount = key_int - 1
      key_number = 1
      key_amt = range(int(amount))
      for i in key_amt:
         letters = string.ascii_letters
         key = f"{key_prefix}-" + ''.join(random.choice(letters) for i in range(6))
         em = discord.Embed(color=0xff0000)
         em.add_field(name=f"Key: {key_number}", value=key)
         await ctx.send(embed=em)
         key_number += 1
         post = {"key": key, "expiration": expires, "user": "Empty", "used": 'unused'}
         collection.insert_one(post)
      key = f"{key_prefix}-" + ''.join(random.choice(letters) for i in range(6))
   
   # -- collection.delete_many({}) #deletes all the keys

   # -- Send all info to discord and database
   message = await ctx.send("Connecting...")
   try:
      if key_int == 1:
         key_yes = key
      else:
         key_yes = f'{key_prefix}-fkEPsG'
         pass

      #sends key info to database
      
      post = {"_license": "Pegasus Predictor™", "key": key, "expiration": expires, "user": "Empty", "used": 'unused'}
      collection.insert_one(post)
      
      em = discord.Embed(color=0x00ff00)
      em = discord.Embed(title="Pegasus Predictor | Key Generation Was Successfull", color=0xff0000)
      em.add_field(name="Key", value=f"```{key}```", inline=True)
      em.add_field(name="Expiration", value=f"```{str(time)}```", inline=True)
      em.set_footer(text=f"Redeem Using /redeem {key}")
      await message.delete()
      await ctx.send(embed=em)
   except:
      em = discord.Embed(color=0xff0000)
      em = discord.Embed(title="Pegasus Predictor | Key Generation Was Unsuccessfull", color=0xff0000)
      em.add_field(name="Details", value=f"```DATABASE.ERROR```", inline=True)
      await ctx.send(content="", embed=em)

#redeem function
@bot.slash_command()
async def redeem(ctx, key):
   mongo_url = mongo_db_link
   cluster = MongoClient(mongo_url)
   db = cluster[f"{databases_name}"]
   collection = db[f"{collection_name}"]
   try:
      results = collection.find({"key": key})
      for results in results:
         if results['key'] == str(key):
            collection.update_one({"key": key}, {"$set":{"user": ctx.author.id}})
            expiration = str(results['expiration'])
            used = str(results['used'])
            if used == 'used':
               em = discord.Embed(title="Pegasus Predictor | Key Redemption Was Unsuccessfull", color=0xff0000)
               em.add_field(name="License", value="f```{key}```", inline=True)
               em.add_field(name="Details", value=f"```LICENSE.USED```", inline=True)
               await ctx.respond(embed=em)
            elif used == 'unused':
               role = role_name
               user = ctx.message.author
               await user.add_roles(discord.utils.get(user.guild.roles, name=role))
               em = discord.Embed(title="Pegasus Predictor | Key Redemption Was Successfull", color=0x00ff00)
               em.add_field(name="License", value=f"```{key}```", inline=True)
               em.add_field(name="Expiration", value=f"```{expiration}```", inline=True)
               await ctx.respond(embed=em)
               collection.update_one({"key": key}, {"$set":{"used": 'used'}})
               return
               
         else:
            em = discord.Embed(title="Pegasus Predictor | Key Redemption Was Unsuccessfull", color=0xff0000)
            em.add_field(name="License", value="f```{key}```", inline=True)
            em.add_field(name="Details", value=f"```LICENSE.INVALID```", inline=True)
            await ctx.respond(embed=em)
   except:
      pass

bot.run('Discord bot token here')
