import asyncio
import random
import os
import json
import discord.ext
from discord.ext.commands import MissingPermissions
import discord
from discord.ext import commands
from discord.interactions import Interaction
import requests
from discord.ui import Select, View, Button, Modal
from discord.commands import Option, SlashCommandGroup
from PIL import Image
from sql_function import *
import yaml
from discord.ext.pages import Paginator, Page
from datetime import timedelta
from datetime import datetime
import re


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

    # user info emojis
    phone = "<:phone:1274727307902455943>"
    partner = "<:partner:1274727306438377594>"
    online = "<:online:1274727305125564557>"
    invisible = "<:invisible:1274727303808815124>"
    idle = "<:idle:1274727302596395028>"
    hypesquad_brilliance = "<:hypesquad_brilliance:1274727325149429792>"
    hypesquad_bravery = "<:hypesquad_bravery:1274727560856735796>"
    hypesquad_balance = "<:hypesquad_balance:1274727321898586144>"
    earlysupporter = "<:earlysupporter:1274727559611027558>"
    dnd = "<:dnd:1274727317528121394>"
    dev = "<:dev:1274727557928976435>"
    bughunter2 = "<:bughunter2:1274727314084724737>"
    bughunter = "<:bughunter:1274727312583163905>"
    botdev = "<:botdev:1274727311186595911>"
    boost = "<:boost:1274727309672452126>"
    staff = "<:staff:1274729786685657118>"
    spotify = "<:spotify:1274729775214104637>"
    
with open("config.yaml", 'r') as f:
    data = yaml.safe_load(f)


#Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=data["Prefix"], intents=intents, activity = discord.Game(name="developed by squidi"))

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


'''
Check if the user has admin rights

Parameters:
-----------
- ctx: Command context
'''
def is_admin():
    async def predicate(ctx):
        if ctx.guild is None:
            return False
        member = ctx.guild.get_member(ctx.author.id)
        if member is None:
            return False
        return member.guild_permissions.administrator

    return commands.check(predicate)


# File formats (required for antu-link system and auto-reaction)
formats = ['png', 'jpg', 'gif' , 'webp', 'jpeg', 'jpg' , 'jpeg' ,'jfif' ,'pjpeg' , 'pjp', 'svg', 'bmp', 'mp4', 'avi', 'mkv', 'mov', 'wmv', '.mp3', 'wav', 'ogg', 'aac', 'flac']


# Embeds that are used multiple times within the bot
class GetEmbed():

    '''
    Parameters:
    ------------
        - embed_index
            If an index is passed which then leads to the correct embed
                0: Bonus XP procentage
                1: User not found 
                2: Help menu main text
                3: Message leaderboard text
                4: Channel for message leaderboard exits
                5: Same channel message leaderboard
                6: Interval has been set
                7: General message leaderboard
                8: Settings message leaderboard
                9: Antilink violation
                10: Error embed for overrides
                11: Mod role (for leaderboard system)
        - settings
            The correct information that must be inserted in the embed
        - settings2 (same as settings)
        - settings3 (same as settings)

    Info:
        - embed_idex must be specified
    '''
    def get_embed(
        embed_index, 
        settings = None, 
        settings2 = None, 
        settings3 = None
        ):

        if embed_index == 0:

            emb = discord.Embed(description=f"""### {Emojis.help_emoji} The bonus XP percentage you want to set is already set
                {Emojis.dot_emoji} The percentage is already set to {settings} %.""", color=bot_colour)


        elif embed_index == 1:

            emb = discord.Embed(description=f"""## The user was not found
                {Emojis.dot_emoji} No entry was found for **{settings}**, so one was created
                {Emojis.dot_emoji} **{settings}** now starts at level 0 with 0 XP""", color=bot_colour)
            
        
        elif embed_index == 2:

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
            
        elif embed_index == 3:
            
            emb = f"""
            {Emojis.dot_emoji} With the dropdown menu below you can select which leaderboard should be sent to this channel
            {Emojis.dot_emoji} The leaderboard differs in the duration after how much time the stats are updated
            {Emojis.help_emoji} You can also select several intervals, in which case several different leaderboards will be sent
            """

        elif embed_index == 4:

            emb = discord.Embed(description=f"""## Channel for the leaderboard has been defined
                {Emojis.dot_emoji} From now on, the leaderboard is sent in {settings}{GetEmbed.get_embed(embed_index=3)}""", color=bot_colour)
        
        elif embed_index == 5:

            emb = discord.Embed(description=f"""## This channel has already been set as a leaderboard channel
                {Emojis.dot_emoji} This channel has already been set for the {'message' if settings == 'message' else 'invite'} leaderboard
                {Emojis.dot_emoji} Would you like to continue setting the {'message' if settings == 'message' else 'invite'} leaderboard (the channel will not be changed) or re-execute the command and set a different channel for the {'message' if settings == 'message' else 'invite'} leaderboard""", color=bot_colour)
    
        elif embed_index == 6:

            emb = discord.Embed(description=f"""## Interval has been set
                {Emojis.dot_emoji} The following leaderboard option{'s' if len(settings) != 1 else ''}
                    {"".join(settings2)}
                {Emojis.dot_emoji} The leaderboard{'s is' if len(settings) == 1 else ''} sent in {settings3}
                {Emojis.help_emoji} The leaderboard only become full leaderboard after the first interval""", color=bot_colour)

        elif embed_index == 7:

            emb = discord.Embed(description=f"""## This is the general leaderboard
                {Emojis.dot_emoji} Here you can see which users have {'written' if settings == 'message' else 'invited'} the most {'messages' if settings == 'message' else 'users'} in total
                {Emojis.help_emoji} It is updated daily and will be edited into the correct leaderboard on <t:{int((datetime.now() + timedelta(days=1)).timestamp())}>""", color=bot_colour)
        
        elif embed_index == 8:

            emb = discord.Embed(description=f"""## Here you can see the settings of the {settings} leaderboard
                {Emojis.dot_emoji} The message leaderboard is currently {'switched off' if settings2[1] == 0 or settings2[1] == None else 'switched on'}.
                {Emojis.dot_emoji} Currently no channel or intervals have been defined for the message leaderboard
                {Emojis.help_emoji} If you want to set the message leaderboard use the `set-{settings}-leaderboard` command""", color=bot_colour)
            
        elif embed_index == 9:

            anti_link_text = {
                0:"discord invitation link",
                1:"link or a discord invitations",
                2:"link or an image / video",
                3:""
            }
            
            emb = discord.Embed(title=f'{Emojis.help_emoji} {settings.author.name} you have violated the anti-link system', 
                description=f"""{Emojis.dot_emoji} You have violated the anti-link system on {settings.guild.name}
                {Emojis.dot_emoji} `You have sent an {anti_link_text[settings2[3]]} to this chat`
                {f"{Emojis.dot_emoji} That's why you got a timeout for {settings2[4]} minutes" if settings2[4] != 0 else ''}""", colour=bot_colour)
            emb.set_footer(text=f'{settings.author.name}', icon_url=settings.author.display_avatar.url if settings.author.display_avatar != None else settings.guild.icon.url)

        elif embed_index == 10:

            emb = discord.Embed(description=f"""## An error has occurred
                {Emojis.dot_emoji} The {settings} could not be overwritten this happens if the option remains unanswered for too long or if I lose the connection
                {Emojis.dot_emoji} If you want {settings2}, you just have to execute the command `/{settings3}` again""", color=bot_colour)
            
        elif embed_index == 11:

            emb = discord.Embed(description=f"""## This role cannot be set as a leaderboard role
                {Emojis.dot_emoji} This role has admin or moderation rights, so it would be too dangerous to assign them through the leaderboard
                {Emojis.help_emoji} If you want to set a different role as leaderboard-role just run the command again""", color=bot_colour)

        return emb
    
    

#########################################  Cancel Button  ########################################


class CancelButton(discord.ui.Button):
    
    def __init__(self, system):
        self.system = system
        super().__init__(
            label = "Cancel setting",
            style = discord.ButtonStyle.danger,
            custom_id = "cancel_button"
        )

    async def callback(self, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            emb = discord.Embed(description=f"""## Setting canceled
                {Emojis.dot_emoji} The setting of the {'system' if self.system == None else self.system} was canceled.
                {Emojis.dot_emoji} If you change your mind, you can always execute the command again.""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class HelpMenu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.slash_command(name = "help", description = "Do you need a small overview!")
    async def help(self, ctx:discord.ApplicationContext):
            
        emb = GetEmbed.get_embed(embed_index = 2)
        
        file = discord.File('assets/images/shiro_help_banner.png', filename='shiro_help_banner.png')
        emb.set_image(url=f"attachment://shiro_help_banner.png")
        await ctx.respond(embed=emb, view=HelpMenuSelect(), file=file)


class HelpMenuSelect(discord.ui.View):

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
            discord.SelectOption(label="Level commands part 2", description="Shows you all commands that belong to the level system part 2", value="level_two"),
            discord.SelectOption(label="Statistics commands", description="Shows you all commands that belong to the statistics system", value="statistic"),
            discord.SelectOption(label="Other system commands", description="Shows you all commands that belong to the other systems", value="other_systems")
        ],
        custom_id = "help_menu_select")
    
    async def help_menue_select(self, select, interaction:discord.Interaction):

        if select.values[0] == "mod":

            emb = discord.Embed(description="## Mod commands", color=bot_colour)
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
            emb.add_field(name="/give-role", 
                value="Gives a user a role chosen by you", inline=True)
            emb.add_field(name="/remove-role", 
                value="Removes a user a role chosen by you", inline=True)

            await interaction.response.send_message(embed=emb, ephemeral=True)
            

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
            await interaction.response.send_message(embed=emb, ephemeral=True)


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
            await interaction.response.send_message(embed=emb, ephemeral=True)


        if select.values[0] == "level_two":

            emb = discord.Embed(description=f"""## Level system commands of part 2""", color=bot_colour)
            emb.add_field(name="/set-level-system", 
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
            await interaction.response.send_message(embed=emb, ephemeral=True)


        if select.values[0] == "statistic":

            emb = discord.Embed(description="""## Statistics system commands """, color=bot_colour)
            emb.add_field(name="set-message-leaderboard",
                value="Set the message leaderboard", inline=True),
            emb.add_field(name="show-message-leaderboard-setting",
                value="Shows you how the message leaderboard is set", inline=True),
            emb.add_field(name="add-message-leaderboard-role",
                value="Specify roles that are assigned to certain places", inline=True),
            emb.add_field(name=" ", value=" ", inline=False),
            emb.add_field(name="remove-message-leaderboard-role",
                value="Removes roles as leaderboard roles", inline=True),
            emb.add_field(name="show-message-leaderboard-roles",
                value="Shows all roles that are set for the leaderbaord", inline=True),
            emb.add_field(name="reset-message-leaderboard-roles",
                value="Resets all leaderboard roles", inline=True),
            emb.add_field(name=" ", value=" ", inline=False),
            emb.add_field(name="show-invites",
                value="Shows how many users have been invited by a specific user", inline=True),
            emb.add_field(name="/userinfo", 
                value="Display all information about a user", inline=True)
            emb.add_field(name="/serverinfo", 
                value="Show all information about your server", inline=True)
            await interaction.response.send_message(embed=emb, ephemeral=True)


        if select.values[0] == "other_systems":

            emb = discord.Embed(description="""## Other system commands""", color=bot_colour)
            emb.add_field(name="set-auto-reaction",
                value="Sets the auto-reaction system", inline=True)
            emb.add_field(name="add-auto-reaction",
                value="Adds auto-reactions to the server", inline=True)
            emb.add_field(name="remove-auto-reaction",
                value="Removes auto-reactions from the server", inline=True)
            emb.add_field(name="", value="", inline=False)
            emb.add_field(name="show-auto-reactions",
                value="Shows all auto-reactions that are set on the server", inline=True)
            emb.add_field(name="reset-auto-reactions",
                value="Resets all auto-reactions that are set for the server", inline=True)
            emb.add_field(name="set-anti-link", 
                value="Set the anti-link system", inline=True)
            emb.add_field(name=" ", value=" ", inline=False)
            emb.add_field(name="/show-antilink-settings", 
                value="Shows how the antilin system is set", inline=True)
            emb.add_field(name="/add-antilink-whitelist", 
                value="Adds items to the whitelist", inline=True)
            emb.add_field(name="/remove-antilink-whitelist", 
                value="Removes items from the whitelist", inline=True)
            emb.add_field(name=" ", value=" ", inline=False)
            emb.add_field(name="/show-antilink-whitelist", 
                value="Shows what is on the white list", inline=True)
            emb.add_field(name="/reset-antilink-whitelist", 
                value="Resets the whitelist", inline=True)
            emb.add_field(name="/ghost-ping-settings", 
                value="Set the ghost ping system", inline=True)
            await interaction.response.send_message(embed=emb, ephemeral=True)


    @discord.ui.button(
            label="✕ Close",
            style=discord.ButtonStyle.blurple,
            custom_id="close_button"
        )
    
    async def callback(self, interaction:Interaction):
        
        await interaction.message.delete()


bot.add_cog(HelpMenu(bot))




