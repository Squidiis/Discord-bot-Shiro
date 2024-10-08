from discord.interactions import Interaction
from utils import *
from typing import Union
from sql_function import DatabaseCheck, DatabaseRemoveDatas, DatabaseUpdates



class AutoReaction(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    '''
    Returns all auto-reactions

    Parameters:
    -----------
        - guild_id
            Id of the server
            
    Info:
        - guild_id must be specified
        - If no auto-reactions are set, information about this is returned
    '''
    async def show_auto_reactions_all(guild_id:int):
        
        all_auto_reactions = await DatabaseCheck.check_auto_reaction(guild_id = guild_id)

        if all_auto_reactions:

            final_reactions = []
            for _, channel, category, parameter, emoji in all_auto_reactions:

                final_reactions.append(f"> {Emojis.dot_emoji} In {f'the channel <#{channel}>' if channel != None else f'the category <#{category}>'}, is responded to {parameter} with the emoji: {emoji}")

            return "\n".join(final_reactions)

        else:

            return f"> {Emojis.dot_emoji} No auto-reactions have been set"
        

    '''
    Checks when the auto-reaction should react

    Parameters:
    -----------
        - parameter
            What to react to
        - message
            Message (specifies the required ids)
            
    Info:
        - parameter and message must both be specified
    '''
    async def should_react(self, parameter:str, message:discord.Message):
    
        if parameter == "links, images and videos":
            return 'https://' in message.content or len(message.attachments) >= 1
        
        elif parameter == "images and videos":
            return 'hettps://' in message.content and any(word in message.content for word in formats) or len(message.attachments) >= 1
        
        elif parameter == "links":
            return 'https://' in message.content
        
        elif parameter == "text messages":
            return 'https://' not in message.content and not any(word in message.content for word in formats) and not message.attachments
        
        elif parameter == "any message":
            return True
        
        return False


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        
        if not message.guild:
            return

        check_settings = await DatabaseCheck.check_bot_settings(guild_id = message.guild.id)

        if check_settings:

            if check_settings[5] == 0:
                return

            recations = await DatabaseCheck.check_auto_reaction(guild_id = message.guild.id)

            if not recations:
                return
            
            for _, channel, category, parameter, emoji in recations:
                
                if (channel is not None and message.channel.id == channel) or (category is not None and message.channel.category_id == category):
                    
                    if await self.should_react(parameter = parameter, message = message) == True:

                        try:

                            await message.add_reaction(emoji = emoji)

                        except Exception as error:
                        
                            print("parameterized query failed {}".format(error))

        else:
            return
    
    
    @commands.Cog.listener()
    async def on_guild_emojis_update(guild, before, after):

        before_emojis = set(before)
        after_emojis = set(after)

        removed_emojis = before_emojis - after_emojis
        
        if removed_emojis:
            for emoji in removed_emojis:
                
                await DatabaseRemoveDatas.remove_auto_reactions(guild_id = guild.id, emoji = emoji)
                

    @commands.slash_command(name = "set-auto-reaction", description = "Set the auto-reaction system!")
    @commands.has_permissions(administrator = True)
    async def set_auto_reaction(self, ctx:discord.ApplicationContext):

        settings = await DatabaseCheck.check_bot_settings(guild_id = ctx.guild.id)

        emb = discord.Embed(description=f"""## Settings menu for the auto reaction system
            {Emojis.dot_emoji} With the button below you can either switch the auto-reactions menu on or off
            {Emojis.dot_emoji} The auto-reaction system is currently {'switched off' if settings[5] == 0 else 'switched on'}
            {Emojis.help_emoji} With the command `add-auto-reaction` you can then set auto-reactions that automatically leave a reaction in the areas you specify""", color=bot_colour)
        await ctx.respond(embed=emb, view = AutoReactionOnOffSwitch())


    @commands.slash_command(name = "add-auto-reaction", description = "Adds an auto-reaction to the server!")
    @commands.has_permissions(administrator = True)
    async def add_auto_reaction(self, ctx:discord.ApplicationContext, 
        area:Option(Union[discord.TextChannel, discord.CategoryChannel], required = True, description="Select in which channel or category the auto-reaction should be created!"), 
        parameter:Option(str, required = True, description="Select what this auto-reaction should react to!",
            choices = ["links, images and videos", "images and videos", "links", "text messages", "any message"]), 
        emoji:Option(str, required = True, description="Enter the emoji you want for this auto-reaction (just insert it and it'll be set)!")):

        check_reaction = await DatabaseCheck.check_auto_reaction(
            guild_id = ctx.guild.id, 
            channel_id = area.id if isinstance(area, discord.TextChannel) else None,
            category_id = None if isinstance(area, discord.TextChannel) else area.id,
            parameter = parameter,
            emoji = emoji
            )
        
        if check_reaction:

            emb = discord.Embed(description=f"""## An auto-reaction role has already been defined that has exactly these parameters
                {Emojis.dot_emoji} There is already an auto-reaction defined for the {f'channel {area.id}' if isinstance(area, discord.TextChannel) else f'category {area.id}'}.
                {Emojis.dot_emoji} This already reacts to {parameter} with the emoji {emoji}""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            await DatabaseUpdates.manage_auto_reaction(
                guild_id = ctx.guild.id, 
                channel_id = area.id if isinstance(area, discord.TextChannel) else None,
                category_id = None if isinstance(area, discord.TextChannel) else area.id,
                parameter = parameter,
                emoji = emoji,
                operation = "add"
                )

            emb = discord.Embed(description=f"""## A new auto-reaction has been defined
                {Emojis.dot_emoji} The new auto-reaction reacts in the {'channel' if isinstance(area, discord.TextChannel) else 'category'} {area.mention}
                {Emojis.dot_emoji} The parameter was set so that the autoreaction should react to {parameter}
                {Emojis.dot_emoji} {emoji} was set as the emoji""", color=bot_colour)
            await ctx.respond(embed=emb)

        
    @commands.slash_command(name = "remove-auto-reaction", description = "Removes an auto-reaction from the server!")
    @commands.has_permissions(administrator = True)
    async def remove_auto_reaction(self, ctx:discord.ApplicationContext, 
        area:Option(Union[discord.TextChannel, discord.CategoryChannel], required = True, 
            description="Select which channel or category you want to remove from the auto-reaction system!")):
        
        auto_reactions = await DatabaseCheck.check_auto_reaction(
            guild_id = ctx.guild.id,
            channel_id = area.id if isinstance(area, discord.TextChannel) else None,
            category_id = area.id if isinstance(area, discord.CategoryChannel) else None
        )
    
        if auto_reactions:

            await DatabaseRemoveDatas.remove_auto_reactions(
                guild_id = ctx.guild.id, 
                channel_id = area.id if isinstance(area, discord.TextChannel) else None, 
                category_id = None if isinstance(area, discord.TextChannel) else area.id
            )

            emb = discord.Embed(description=f"""## The auto-reaction has been successfully removed
                {Emojis.dot_emoji} The auto-reaction that was set for the {f'channel' if isinstance(area, discord.TextChannel) else f'category'} <#{area.id}> has been removed
                {Emojis.dot_emoji} With the button below you can see which auto-reactions are still set""", color=bot_colour)
            await ctx.respond(embed=emb, view = ShowAutoReactions())

        else:
            
            emb = discord.Embed(description=f"""## This auto-reaction could not be removed
                {Emojis.dot_emoji} This auto-reaction could not be removed because it is not set as an auto-reaction
                {Emojis.dot_emoji} Here you can see all auto-reactions that are set for this server
                
                {await self.show_auto_reactions_all(guild_id = ctx.guild.id)}""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "show-auto-reactions", description = "Shows all auto-reactions that are available for the server!")
    @commands.has_permissions(administrator = True)
    async def show_auto_reactions(self, ctx:discord.ApplicationContext):
        
        all_auto_reactions = await DatabaseCheck.check_auto_reaction(guild_id = ctx.guild.id)
        
        if all_auto_reactions:

            emb = discord.Embed(description=f"""## Current auto-reactions
                {Emojis.dot_emoji} Here you can see all auto-reactions that have been set for the server {ctx.guild.name}
                
                {await self.show_auto_reactions_all(guild_id = ctx.guild.id)}""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            emb = discord.Embed(description=f"""## No auto-reactions were found
                {Emojis.dot_emoji} No auto-reactions have been set for this server
                {Emojis.help_emoji} If you want to set some use the commad `add-auto-reactions`""", color=bot_colour)
            await ctx.respond(embed = emb)
    
    @commands.slash_command(name = "reset-auto-reactions", description = "Resets all auto-reactions of the server!")
    @commands.has_permissions(administrator = True)
    async def reset_auto_reactions(self, ctx:discord.ApplicationContext):

        all_auto_reactions = await DatabaseCheck.check_auto_reaction(guild_id = ctx.guild.id)

        if all_auto_reactions:

            await DatabaseRemoveDatas.remove_auto_reactions(guild_id = ctx.guild.id)

            emb = discord.Embed(description=f"""## Auto-reactions have been reset
                {Emojis.dot_emoji} All auto-reactions have been deleted
                {Emojis.dot_emoji} If you want to set new auto-reactions you can use the `add-auto-reaction` command to do so""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            emb = discord.Embed(description=f"""## No entries found
                {Emojis.dot_emoji} No auto-reactions could be deleted because none have been set
                {Emojis.dot_emoji} If you want to set some you can use the `add-auto-reaction` command to do so""", color=bot_colour)
            await ctx.respond(embed=emb)


def setup(bot):
    bot.add_cog(AutoReaction(bot))



class AutoReactionOnOffSwitch(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)


    @discord.ui.button(
        label="on / off switch",
        style=discord.ButtonStyle.blurple,
        custom_id="on_off_switch_auto_reaction")
    
    async def auto_reaction_settings(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            settings = await DatabaseCheck.check_bot_settings(guild_id = interaction.guild.id)
            await DatabaseUpdates.update_bot_settings(guild_id = interaction.guild.id, auto_reaction = 1 if settings[5] == 0 else 0)

            emb = discord.Embed(description=f"""## The auto reaction system is now {'activated' if settings[5] == 0 else 'deactivated'}.
                {Emojis.dot_emoji} {'From now on, reactions will be assigned automatically according to the previously set parameters' if settings[5] == 0 else 'From now on, no new reactions will be added automatically'}
                {Emojis.dot_emoji} If you want to set the system further, you can simply run the `set-auto-reaction` again""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=None)
        
        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class ShowAutoReactions(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button( 
        label="show auto-reactions",
        style=discord.ButtonStyle.blurple,
        custom_id="show_all_auto_reactions"
        )

    async def show_auto_reactions_button(self, button, interaction: Interaction):
        
        if interaction.user.guild_permissions.administrator:

            emb = discord.Embed(description=f"""## Auto reactions
                {Emojis.dot_emoji} Here you can see a list of all auto-reactions that have been set for the server {interaction.guild.name} 
                
                {await AutoReaction.show_auto_reactions_all(guild_id = interaction.guild.id)}""", color=bot_colour)
            await interaction.response.edit_message(embed=emb)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)
