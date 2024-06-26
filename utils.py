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


# Embeds that are used multiple times within the bot
class GetEmbed():
    '''
    :embed_idex:
        - If an index is passed which then leads to the correct embed
            0 = Bonus XP procentage
            1 = User not found 
    '''
    def get_embed(embed_index, settings):

        if embed_index == 0:

            emb = discord.Embed(description=f"""### {Emojis.help_emoji} The bonus XP percentage you want to set is already set
                {Emojis.dot_emoji} The percentage is already set to {settings} %.""", color=bot_colour)


        elif embed_index == 1:

            emb = discord.Embed(description=f"""## The user was not found
                {Emojis.dot_emoji} No entry was found for **{settings}**, so one was created
                {Emojis.dot_emoji} **{settings}** now starts at level 0 with 0 XP""", color=bot_colour)
            
        return emb
    



class HelpMenu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.slash_command(name = "help", description = "Do you need a small overview!")
    async def help(self, ctx:discord.ApplicationContext):
            
        emb = discord.Embed(description=f"""# {Emojis.settings_emoji} Help menu
            {Emojis.dot_emoji} Here you can see all the commands that {bot.user.name} has
            ```Please use the Buttons below to explore the\ncorresponding commands```\n### Table of contents:
            > {Emojis.dot_emoji} Mod commands
            > {Emojis.dot_emoji} Fun commands
            > {Emojis.dot_emoji} Level System commands part 1
            > {Emojis.dot_emoji} Level System commands part 2

            **Bot links:**
            {Emojis.dot_emoji} Support server: https://discord.gg/9kJaPrWdwM
            {Emojis.dot_emoji} Githup: https://github.com/Squidiis
            """, color=bot_colour)
        
        file = discord.File('assets/images/shiro_help_banner.png', filename='shiro_help_banner.png')
        emb.set_image(url=f"attachment://shiro_help_banner.png")
        await ctx.respond(embed=emb, view=HelpMenüSelect(), file=file)


class HelpMenüSelect(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder = "Choose from which system you want to see the help menu!",
        max_values = 1,
        min_values = 1,
        options = [
            discord.SelectOption(label="Mod commands", description="Shows you all commands that belong to the mod system", value="mod"),
            discord.SelectOption(label="Fun commands", description="Shows you all commands that belong to the Fun system", value="fun"),
            discord.SelectOption(label="Level commands part 1", description="Shows you all commands that belong to the level system part 1", value="level_one"),
            discord.SelectOption(label="Level commands part 2", description="Shows you all commands that belong to the level system part 2", value="level_two")
        ],
        custom_id = "help_menu_select")
    async def help_menue_select(self, select, interaction:discord.Interaction):

        if select.values[0] == "mod":

            emb = discord.Embed(description="## Mod commands", color=bot_colour)
            emb.add_field(name="set-anti-link", 
                value="Set the anti-link system", inline=True)
            emb.add_field(name="/show-antilink-settings", 
                value="Shows how the antilin system is set", inline=True)
            emb.add_field(name="/add-antilink-whitelist", 
                value="Adds items to the whitelist", inline=True)
            emb.add_field(name=" ", value=" ", inline=False)
            emb.add_field(name="/remove-antilink-whitelist", 
                value="Removes items from the whitelist", inline=True)
            emb.add_field(name="/show-antilink-whitelist", 
                value="Shows what is on the white list", inline=True)
            emb.add_field(name="/reset-antilink-whitelist", 
                value="Resets the whitelist", inline=True)
            emb.add_field(name=" ", value=" ", inline=False)
            emb.add_field(name="/ban", 
                value="Ban a user", inline=True)
            emb.add_field(name="/unban", 
                value="Cancel the ban of a user", inline=True)
            emb.add_field(name="/kick", 
                value="Kick a user", inline=True)
            emb.add_field(name=" ", value=" ", inline=False)
            emb.add_field(name="/timeout", 
                value="Give a user a timeout", inline=True)
            emb.add_field(name="remove-timeout", 
                value="Cancel the timeout of a user", inline=True)
            emb.add_field(name="/clear", 
                value="Delete messages in a channel", inline=True)
            emb.add_field(name=" ", value=" ", inline=False)
            emb.add_field(name="/ghost-ping-settings", 
                value="Set the ghost ping system", inline=True)
            emb.add_field(name="/userinfo", 
                value="Display all information about a user", inline=True)
            emb.add_field(name="/serverinfo", 
                value="Show all information about your server", inline=True)
            await interaction.response.edit_message(embed=emb, attachments=[])
            

        if select.values[0] == "fun":

            emb = discord.Embed(description=f"""## Fun commands""", color=bot_colour)
            emb.add_field(name="/rps", 
                value="Play rock, paper, scissors", inline=True)
            emb.add_field(name="/coinflip", 
                value="Flip a coin", inline=True)
            emb.add_field(name="/cocktails", 
                value="Get a random cocktail recipe", inline=True)
            emb.add_field(name=" ", value=" ", inline=False)
            emb.add_field(name="/animememe", 
                value="Show you a random anime meme", inline=True)
            emb.add_field(name="/anime gif (tag)",
                value="Tags: kiss, hug, lick, feed, idk, dance, slap, fbi, embarres, pet", inline=True)
            await interaction.response.edit_message(embed=emb, attachments=[])


        if select.values[0] == "level_one":

            emb = discord.Embed(description=f"""## Level system commands from part 1""", color=bot_colour)
            emb.add_field(name="/give-xp", 
                value="Give a user XP", inline=True)
            emb.add_field(name="/remove-xp", 
                value="Remove XP from a user", inline=True)
            emb.add_field(name="/give-level", 
                value="Enter a user level", inline=True)
            emb.add_field(name=" ", value=" ", inline=False)
            emb.add_field(name="/remove-level", 
                value="Remove a user level", inline=True)
            emb.add_field(name="/reset-level", 
                value="Reset the level of all users", inline=True)
            emb.add_field(name="/reset-user-stats", 
                value="Reset the level of a user", inline=True)
            emb.add_field(name=" ", value=" ", inline=False)
            emb.add_field(name="/rank", 
                value="Shows which level a user is", inline=True)
            emb.add_field(name="/leaderboard-level", 
                value="Shows 10 users with the highest level", inline=True)
            emb.add_field(name="/add-level-blacklist", 
                value="Add something to the level blacklist", inline=True)
            emb.add_field(name=" ", value=" ", inline=False)
            emb.add_field(name="/remove-level-blacklist", 
                value="Remove something from the level blacklist", inline=True)
            emb.add_field(name="/show-level-blacklist", 
                value="Shows you the level blacklist", inline=True)
            emb.add_field(name="/reset-level-blacklist", 
                value="Resets the level blacklist", inline=True)
            await interaction.response.edit_message(embed=emb, attachments=[])


        if select.values[0] == "level_two":

            emb = discord.Embed(description=f"""## Level system commands of part 2""", color=bot_colour)
            emb.add_field(name="/level-system-settings", 
                value="Set the level system", inline=True)
            emb.add_field(name="/add-level-role", 
                value="Define roles as level roles", inline=True)
            emb.add_field(name="/remove-level-role", 
                value="Remove role as level roles", inline=True)
            emb.add_field(name=" ", value=" ", inline=False)
            emb.add_field(name="/show-level-roles", 
                value="Shows you all level roles", inline=True)
            emb.add_field(name="/reset-level-roles", 
                value="Reset all level roles", inline=True)
            emb.add_field(name="/add-bonus-xp-list", 
                value="Add items to the bonus XP list", inline=True)
            emb.add_field(name=" ", value=" ", inline=False)
            emb.add_field(name="/remove-bonus-xp-list", 
                value="Remove items from the bonus xp list", inline=True)
            emb.add_field(name="/show-bonus-xp-list", 
                value="Shows you the bonus xp list", inline=True)
            emb.add_field(name="/reset-bonus-xp-list", 
                value="Resets the bonus xp list", inline=True)
            await interaction.response.edit_message(embed=emb, attachments=[])


    @discord.ui.button(label="<- Back", style=discord.ButtonStyle.gray, custom_id="back_button")
    async def back_help_button(self, button, interaction:discord.Interaction):

        emb = discord.Embed(description=f"""# {Emojis.settings_emoji} Help menu
            {Emojis.dot_emoji} Here you can see all the commands that {bot.user.name} has
            ```Please use the Buttons below to explore the\ncorresponding commands```\n### Table of contents:
            > {Emojis.dot_emoji} Mod commands
            > {Emojis.dot_emoji} Fun commands
            > {Emojis.dot_emoji} Level System commands part 1
            > {Emojis.dot_emoji} Level System commands part 2

            **Bot links:**
            {Emojis.dot_emoji} Support server: https://discord.gg/9kJaPrWdwM
            {Emojis.dot_emoji} Githup: https://github.com/Squidiis
            """, color=bot_colour)
        
        file = discord.File('assets/images/shiro_help_banner.png', filename='shiro_help_banner.png')
        emb.set_image(url=f"attachment://shiro_help_banner.png")
        await interaction.response.edit_message(embed=emb, view=HelpMenüSelect(), file=file)


bot.add_cog(HelpMenu(bot))




