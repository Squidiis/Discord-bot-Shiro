import asyncio
import random
import os
import json
import discord.ext
from discord.ext.commands import MissingPermissions
import discord
from discord.ext import commands
import mysql.connector
from datetime import *
import requests
from discord.ui import Select, View, Button, Modal
from discord.commands import Option, SlashCommandGroup
from PIL import Image
from sql_function import *
import yaml
from discord.ext.pages import Paginator, Page

"""
┏━━━┓ ┏━━━┓ ┏┓ ┏┓ ┏━━┓ ┏━━━┓ ┏━━┓
┃┏━┓┃ ┃┏━┓┃ ┃┃ ┃┃ ┗┫┣┛ ┗┓┏┓┃ ┗┫┣┛
┃┗━━┓ ┃┃ ┃┃ ┃┃ ┃┃  ┃┃   ┃┃┃┃  ┃┃
┗━━┓┃ ┃┗━┛┃ ┃┃ ┃┃  ┃┃   ┃┃┃┃  ┃┃
┃┗━┛┃ ┗━━┓┃ ┃┗━┛┃ ┏┫┣┓ ┏┛┗┛┃ ┏┫┣┓
┗━━━┛    ┗┛ ┗━━━┛ ┗━━┛ ┗━━━┛ ┗━━┛
"""


# These are all emojis used in this bot the individual eimojis are stored again in this folder: discord_bot/emojis
class Emojis:

    arrow_emoji = "<a:shiro_arrow:1092443788900831355>"
    fail_emoji = "<a:shiro_failed:1092862110381383762>"
    dot_emoji = "<:shiro_dot_blue:1092871145075781662>"
    settings_emoji = "<a:shiro_settings:1092871148494143499>"
    help_emoji = "<:shiro_help:1092872576017109033>"
    exclamation_mark_emoji = "<a:shiro_important:1092870970785665055>"
    succesfully_emoji = "<a:shiro_successful:1092862166702510290>"
        
with open("config.yaml", 'r') as f:
    data = yaml.safe_load(f)


#Intents
intent = discord.Intents.default()
intent.members = True
intents = discord.Intents.all()

bot = commands.Bot(command_prefix=data["Prefix"], intents=intents)



# The red colour for the fail / error embeds
error_red = discord.Colour.brand_red()


# The bot color, each embed has this color
bot_colour = data["Bot_colour"]


# Fail / error embeds
no_permissions_emb = discord.Embed(title=f"You are not authorized {Emojis.fail_emoji}", 
    description = f"You are not allowed to press this button only admins are allowed to interact with this command",color = error_red)

user_bot_emb = discord.Embed(title = f"The user is a bot {Emojis.fail_emoji}", 
    description = f"The user you have selected is a bot and cannot be selected in this command!", color = error_red)

user_not_found_emb = discord.Embed(title=f"The user was not found {Emojis.fail_emoji}", 
    description = f"{Emojis.dot_emoji} No entry was found the user is also no longer on the server", color = error_red)

no_entry_emb = discord.Embed(title=f"{Emojis.help_emoji} No entry found", 
    description = f"{Emojis.dot_emoji} Therefore, one was created just try again.", color = bot_colour)

# default message for level up message system
default_message = 'Oh nice {user} you have a new level, your newlevel is {level}' 


class GetEmbed():
    '''
    :embed_idex:
        - If an index is passed which then leads to the correct embed
            0 = Bonus XP procentage
            1 = User not found 
    '''
    def get_embed(embed_index, settings):

        if embed_index == 0:

            emb = discord.Embed(description=f"""### {Emojis.help_emoji} Der bonus XP Prozentsatz den du festlegen willst ist bereist festgelegt
                {Emojis.dot_emoji} Der Prozentsatz ist beits auf {settings} % festgelegt.""", color=bot_colour)


        elif embed_index == 1:

            emb = discord.Embed(description=f"""## The user was not found
                {Emojis.dot_emoji} No entry was found for **{settings}**, so one was created
                {Emojis.dot_emoji} **{settings}** now starts at level 0 with 0 XP""", color=bot_colour)
            
        return emb
    





# Help Commands
#TODO Ein Inhaltsverzeichnis auf die erste seite 
class HelpMenu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.pages = [

            # Mod commands
            Page(embeds=[discord.Embed(title="Mod Commands", 
                description="All mod commands are listed on this page", color=bot_colour)
                .add_field(name="set-anti-link", 
                    value="Set the anti-link system, you can choose if only dischrd invitation links should be deleted, if everything except pictures and videos should be deleted or if everything should be deleted", inline=False)
                .add_field(name="/ban", 
                    value="Ban a user from your server who will not be able to join again", inline=False)
                .add_field(name="/unban", 
                    value="Unban a user from your server who can then rejoin the server", inline=False)
                .add_field(name="/kick", 
                    value="Kick a user from your server", inline=False)
                .add_field(name="/timeout", 
                    value="Send a user to a timeout you decide how long he needs a timeout", inline=False)
                .add_field(name="remove-timeout", 
                    value="Cancel the timeout of a user who can then write messages normally again", inline=False)
                .add_field(name="/clear", 
                    value="Delete messages you can freely specify how many should be deleted", inline=False)
                .add_field(name="/ghost-ping-settings", 
                    value="Set the anti ghost ping system when someone tags another user and then deletes the message, a message is sent stating what the user wrote and who they tagged", inline=False)
                .add_field(name="/userinfo", 
                    value="Display all important information about a user", inline=False)
                .add_field(name="/serverinfo", 
                    value="Show all important information about your server", inline=False)
                ]),

            # Fun commands
            Page(embeds=[discord.Embed(title="Fun commands", 
                description="All fun commands are listed here on this page", color=bot_colour)
                .add_field(name="/rps", 
                    value="Play rock, paper, scissors against the bot or another user", inline=False)
                .add_field(name="/coinflip", 
                    value="Flip a coin either heads or tails", inline=False)
                .add_field(name="/cocktails", 
                    value="Get a random cocktail recipe", inline=False)
                .add_field(name="/animememe", 
                    value="Show you a random anime meme from reddit", inline=False)
                .add_field(name="Role play commands", 
                    value="Here are all Role play commands", inline=False)
                .add_field(name="/anime gif (tag)",
                    value="Tags: kiss, hug, lick, feed, idk, dance, slap, fbi, embarres, pet", inline=False)
                ]),

            Page(embeds=[discord.Embed(title="Level System commands Teil 1",
                description="""Hier sihst du alle level system commands""", color=bot_colour)
                .add_field(name="/give-xp", value="", inline=False)
                .add_field(name="/remove-xp", value="", inline=False)
                .add_field(name="/give-level", value="", inline=False)
                .add_field(name="/remove-level", value="", inline=False)
                .add_field(name="/reset-level", value="", inline=False)
                .add_field(name="/reset-user-stats", value="", inline=False)
                .add_field(name="/rank", value="", inline=False)
                .add_field(name="/leaderboard-level", value="", inline=False)
                ]),
            
            Page(embeds=[discord.Embed(title="Level System commands Teil 2", 
                description="""Hier sind alle level system commands""", color=bot_colour)
                .add_field(name="/level-system-settings", value="", inline=False)
                .add_field(name="/reset-level-blacklist", value="", inline=False)
                .add_field(name="/add-level-blacklist", value="", inline=False)
                .add_field(name="/remove-level-blacklist", value="", inline=False)
                .add_field(name="/show-level-blacklist", value="", inline=False)
                .add_field(name="/add-level-role", value="", inline=False)
                .add_field(name="/remove-level-role", value="", inline=False)
                .add_field(name="/show-level-roles", value="", inline=False)
                .add_field(name="/add-bonus-xp-list", value="", inline=False)
                .add_field(name="/remove-bonus-xp-list", value="", inline=False)
                .add_field(name="/show-bonus-xp-list", value="", inline=False)
                .add_field(name="/reset-bonus-xp-list", value="", inline=False)
                ])]

    def get_pages(self):
        return self.pages
    
    
    @commands.slash_command(name = "help", description = "Do you need a little help!")
    async def help(self, ctx:discord.ApplicationContext):
        
        
        paginator = Paginator(pages=self.get_pages())

        embed = discord.Embed(description="stuff3")
        embed.add_field(name="meddl", value="meddl leute")

        self.pages.append(embed)
        await paginator.respond(ctx.interaction)
     
bot.add_cog(HelpMenu(bot))




