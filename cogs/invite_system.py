from discord.interactions import Interaction
from utils import *
from sql_function import *
from discord.ext import tasks
import pytz

class Messageleaderboard(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name = "set-message-leaderboard", description = "Set the message leaderboard system!")
    async def set_message_leaderboard(self, ctx:discord.ApplicationContext):

        settings = DatabaseCheck.check_leaderboard_settings(guild_id = ctx.guild_id)

        emb = discord.Embed(description=f"""## Set the message leaderboard
            {Emojis.dot_emoji} With the lower select menu you can define a channel in which the leaderboard should be sent
            {Emojis.dot_emoji} Then you can also set an interval at which time intervals the leaderboard should be updated
            {Emojis.dot_emoji} You can also switch the system off or on currently it is {'switched off' if settings[0] else 'switched on'}. (as soon as it is switched off, no more messages are counted and when it is switched on, the leaderboard is reset)
            {Emojis.help_emoji} The leaderboard is edited when you update it, so you should make sure that no one else can write in the channel you specified""", color=bot_colour)        
        await ctx.respond(embed=emb, view=SetleaderboardChannel())


    @commands.slash_command(name = "show-message-leaderboard-setting", description = "All show you how the message leaderboard is set!")
    async def show_message_leaderboard_settings(self, ctx:discord.ApplicationContext):
        
        settings = DatabaseCheck.check_leaderboard_settings(guild_id = ctx.guild.id)

        intervals = {
            settings[2]:"Daily",
            settings[3]:"Weekly",
            settings[4]:"Monthly"
        }
        intervals_text = []
        for i in settings[2], settings[3], settings[4]:

            if i != None:

                intervals_text.append(f"{Emojis.dot_emoji} {intervals[i]} updating Message leaderboard\n")

        emb = discord.Embed(description=f"""## Here you can see all the settings of the message leaderboard
            {Emojis.dot_emoji} {f'Currently <#{settings[5]}> is set as' if settings[5] != None else 'No'} message leaderboard channel has been set
            {Emojis.dot_emoji} The following intervals are currently defined for which a leaderboard exists:
            {"".join(intervals_text) if intervals_text != [] else f'{Emojis.dot_emoji} No intervals have been defined yet'}""", color=bot_colour)
        await ctx.respond(embed = emb)


    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        
        check = DatabaseCheck.check_leaderboard_settings(guild_id = message.guild.id)

        if message.author.bot:
            return
        
        if check[1] == 1:
            
            DatabaseUpdates.manage_leaderboard(guild_id = message.guild.id, user_id = message.author.id, interval = "count")


    @commands.Cog.listener()
    async def on_message_delete(self, message:discord.Message):

        check = DatabaseCheck.check_leaderboard_settings(guild_id = message.guild.id)

        if check[1] == 1:

            if message.id == check[2]:

                DatabaseUpdates.manage_leaderboard(guild_id = message.guild.id, back_to_none = "daily")

            elif message.id == check[3]:

                DatabaseUpdates.manage_leaderboard(guild_id = message.guild.id, back_to_none = "weekly")


            elif message.id == check[4]:

                DatabaseUpdates.manage_leaderboard(guild_id = message.guild.id, back_to_none = "monthlyv")


    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):

        check = DatabaseCheck.check_leaderboard_settings(guild_id = channel.guild.id)

        if check[5] == channel.id:

            DatabaseRemoveDatas._remove_leaderboard_settings(guild_id = channel.guild.id)

    
def setup(bot):
    bot.add_cog(Messageleaderboard(bot))


async def sort_leaderboard(user_list, interval):

    max_lengths = [
        max(len(str(t[i])) for t in user_list)
        for i in range(6)
    ]
    
    user_names = []
    for t in user_list:

        user = await bot.get_or_fetch_user(t[1])
        user_names.append(user.name)
        max_lengths[0] = max(max_lengths[0], len(user.name))
    
    padded_tuples = [
        (
            user_names[i].ljust(max_lengths[0]), 
            str(t[1]).ljust(max_lengths[1]),
            str(t[2]).ljust(max_lengths[2]),
            str(t[3]).ljust(max_lengths[3]),
            str(t[4]).ljust(max_lengths[4])
        )
        for i, t in enumerate(user_list)
    ]

    leaderboard = []
    for i in range(min(len(user_list), 15)):
        num_str = str(i + 1)
        if len(num_str) == 1:
            num_str = f" #{num_str}  "
        elif len(num_str) == 2:
            num_str = f" #{num_str} "

        leaderboard.append(f"`{num_str}` `{padded_tuples[i][0]}` `messages {padded_tuples[i][interval]}`\n")

    return "".join(leaderboard)


@tasks.loop(hours=1)
async def edit_leaderboard(bot):

    for guild in bot.guilds:

        leaderboard_settings = DatabaseCheck.check_leaderboard_settings(guild_id = guild.id)

        if leaderboard_settings:

            if leaderboard_settings[1] == 1:
                message_ids = [
                    ("1_day_old", leaderboard_settings[2]),
                    ("1_week_old", leaderboard_settings[3]),
                    ("1_month_old", leaderboard_settings[4])
                ]
                
                if leaderboard_settings[1] == 1 and leaderboard_settings[5] != None:

                    try:
                        
                        current_date = datetime.now(UTC)

                        for message_name, message_id in message_ids:

                            if message_id != None:
                                
                                channel = bot.get_channel(leaderboard_settings[5])
                                message = await channel.fetch_message(message_id)

                                message_age = message.edited_at if message.edited_at != None else message.created_at

                                if leaderboard_settings[2] != None:

                                    if (current_date - message_age) > timedelta(days=1) and message_name == "1_day_old":

                                        user_list = DatabaseCheck.check_leaderboard(guild_id = guild.id, interval = 0)
                                        users = await sort_leaderboard(user_list=user_list, interval=3)
                                        emb = discord.Embed(description=f"""## Daily Messages Leaderboard
                                            {users}""", color=bot_colour)

                                        await message.edit(embed = emb)

                                if leaderboard_settings[3] != None:

                                    if (current_date - message_age) > timedelta(weeks=1) and message_name == "1_week_old":
                                        
                                        user_list = DatabaseCheck.check_leaderboard(guild_id = guild.id, interval = 1)
                                        users = await sort_leaderboard(user_list=user_list, interval=3)
                                        emb = discord.Embed(description=f"""## Weekly Messages Leaderboard
                                            {users}""", color=bot_colour)

                                        await message.edit(embed = emb)

                                if leaderboard_settings[4] != None:

                                    if (current_date - message_age) > timedelta(days=30) and message_name == "1_month_old":
                                        
                                        user_list = DatabaseCheck.check_leaderboard(guild_id = guild.id, interval = 2)
                                        users = await sort_leaderboard(user_list=user_list, interval=4)
                                        emb = discord.Embed(description=f"""## Monthly Messages Leaderboard (30 days)
                                            {users}""", color=bot_colour)

                                        await message.edit(embed = emb)

                    except Exception as error:
                        print("parameterized query failed {}".format(error))


class SetleaderboardChannel(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(LeaderboardOnOffSwitch())
        self.add_item(CancelButton(system = "message leaderboard system"))

    @discord.ui.channel_select(
        placeholder = "Choose a channel that you want to set as the leaderboard channel!",
        min_values = 1,
        max_values = 1,
        custom_id = "leaderboard_channel_select",
        channel_types = [
            discord.ChannelType.text, 
            discord.ChannelType.forum, 
            discord.ChannelType.news
        ]
    )

    async def set_leaderboard_channel(self, select, interaction:discord.Interaction):
        
        settings = DatabaseCheck.check_leaderboard_settings(guild_id = interaction.guild.id)

        if settings:

            if settings[5] == select.values[0].id:

                await interaction.response.edit_message(embed=GetEmbed.get_embed(embed_index=4), view=ContinueSetting())

            else:
                
                emb = discord.Embed(description=f"""## A channel has already been defined for the leaderboard
                    {Emojis.dot_emoji} Would you like to overwrite this?
                    {Emojis.dot_emoji} Currently is <#{settings[5]}> set as the channel for the leaderboard""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=OverwriteChannel(channel_id=select.values[0].id))

        else:

            DatabaseUpdates.create_leaderboard_settings(guild_id = interaction.guild.id, settings = "create", channel_id = select.values[0].id)

        emb = discord.Embed(description=f"""## Channel for the leaderboard has been defined
            {Emojis.dot_emoji} From now on, the leaderboard is sent in {select.values[0].mention}
            {GetEmbed.get_embed(embed_index=3)}
            """, color=bot_colour)
        await interaction.response.edit_message(embed=emb, view=Setleaderboard())


    @discord.ui.button(
        label="skip channel setting",
        style=discord.ButtonStyle.blurple,
        custom_id="skip_channel"
    )
    async def skip_set_channel(self, button, interaction:discord.Interaction):
        
        if DatabaseCheck.check_leaderboard_settings(guild_id = interaction.guild.id)[5]:

            emb = discord.Embed(description=f"""## Setting the channel was skipped
                {GetEmbed.get_embed(embed_index=3)}""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=Setleaderboard())

        else:

            emb = discord.Embed(description=f"""## Setting cannot be skipped
                {Emojis.dot_emoji} The setting can only be skipped if a channel has been assigned to the message leaderboard
                {Emojis.dot_emoji} You must first set a channel before you can continue""", color=bot_colour)
            await interaction.response.send_message(embed=emb, view=None, ephemeral=True)


class Setleaderboard(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CancelButton(system = "message leaderboard system"))

    def compare_lists(self, list1, list2):

        sorted_list1 = sorted(list1, key=lambda x: (x is None, x))
        sorted_list2 = sorted(list2, key=lambda x: (x is None, x))

        return sorted_list1 == sorted_list2


    @discord.ui.select(
        placeholder = "Select the intervals at which the activities should be displayed!",
        min_values = 1,
        max_values = 3,
        custom_id = "set_leaderboard",
        options = [
            discord.SelectOption(label="Update daily", description="The leaderboard is updated every day", value="daily"),
            discord.SelectOption(label="Update weekly", description="The leaderboard is updated every week", value="weekly"),
            discord.SelectOption(label="Update monthly", description="The leaderboard is updated every month", value="monthly")
        ]
    )
    
    async def set_leaderboard_select(self, select, interaction:discord.Interaction):

        text_dict = {
            "daily":"one day",
            "weekly":"one week",
            "monthly":"one month"
        }

        settings = DatabaseCheck.check_leaderboard_settings(guild_id = interaction.guild.id)
        check_list = []
        if any(elem is not None for elem in [settings[2], settings[3], settings[4]]):
            
            if self.compare_lists(list1=select.values, list2=[settings[2], settings[3], settings[4]]):

                emb = discord.Embed(description=f"""## These intervals are already set
                    {Emojis.dot_emoji} You have already defined these intervals for the message leaderboard
                    {Emojis.help_emoji} If you want to have other intervals you can simply execute this command again and overwrite them""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=None)

            else:

                for i in select.values[0]:

                    if i in [settings[2], settings[3], settings[4]]:

                        check_list.append(f"{Emojis.dot_emoji} {i} update\n")

                emb = discord.Embed(description=f"""## Intervals have already been defined
                    {Emojis.dot_emoji} The following intervals are currently active:
                        {check_list}
                    {Emojis.dot_emoji} Do you want to overwrite them?""", color=bot_colour)
                await interaction.response.edit_message(embed=emb)

        else:

            option_list, check_list = [], []
            for i in select.values:
                option_list.append(f"{Emojis.dot_emoji} {i} update\n")
                check_list.append(i)

                if i != None:

                    emb = discord.Embed(
                        description=f"""## The number of messages is saved for {text_dict[i]}.
                            {Emojis.dot_emoji} When the time is up, this message will be edited into a leaderboard showing the users who have written the most messages""", color=bot_colour)

                    channel = bot.get_channel(settings[5])
                    message = await channel.send(embed=emb)
                    
                    DatabaseUpdates.manage_leaderboard(guild_id = interaction.guild.id, settings = i, message_id = message.id)

            for i in [value for value in ["daily", "weekly", "monthly"] if value not in check_list]:

                DatabaseUpdates.manage_leaderboard(guild_id = interaction.guild.id, back_to_none = i)

            emb = discord.Embed(description=f"""## Interval has been set
                {Emojis.dot_emoji} The following leaderboard option{'s' if len(select.values) != 1 else ''}
                    {"".join(option_list)}
                {Emojis.dot_emoji} The leaderboard{'s is' if len(select.values) == 1 else ''} sent in <#{DatabaseCheck.check_leaderboard_settings(guild_id = interaction.guild.id)[5]}>
                {Emojis.help_emoji} The leaderboard only become full leaderboard after the first interval""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=None)


    @discord.ui.button(
        label="skip interval setting",
        style=discord.ButtonStyle.blurple,
        custom_id="skip_interval"
    )
    async def skip_set_channel(self, button, interaction:discord.Interaction):
        
        interval = DatabaseCheck.check_leaderboard_settings(guild_id = interaction.guild.id)

        intervals = {
            interval[2]:"daily",
            interval[3]:"weekly",
            interval[4]:"monthly"
        }

        if interval[2] or interval[3] or interval[4]:
            
            check_interval = "".join([intervals[i] for i in [interval[2], interval[3], interval[4]] if i is not None])

            emb = discord.Embed(description=f"""## Setting the intervals was skipped
                {Emojis.dot_emoji} {f'The intervals {check_interval} will be kept as intervals' if len(check_interval) != 1 else f'The interval {check_interval} will be kept'}""", color=bot_colour)
            
        else:

            emb = discord.Embed(description=f"""## Setting cannot be skipped
                {Emojis.dot_emoji} The setting can only be skipped if at least one interval has been assigned to the message leaderboard
                {Emojis.dot_emoji} You must first set an interval before you can continue""", color=bot_colour)
            await interaction.response.send_message(embed=emb, view=None, ephemeral=True)



class OverwriteChannel(discord.ui.View):

    def __init__(
            self, channel_id):
        super().__init__(timeout=None)
        self.channel_id = channel_id
        self.add_item(CancelButton(system = "message leaderboard system"))

    @discord.ui.button(
        label="overwrite channel",
        style=discord.ButtonStyle.blurple,
        custom_id="overwrite_channel"
    )

    async def overwrite_channel(self, button, interaction:discord.Interaction):
        
        if self.channel_id == None:

            emb = discord.Embed(description=f"""## An error has occurred
                {Emojis.dot_emoji} The channel could not be overwritten this happens if the option remains unanswered for too long or if I lose the connection
                {Emojis.dot_emoji} If you want to set the leaderboard further, you just have to execute the command `/set-message-leaderboard` again""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=None)

        elif self.channel_id == DatabaseCheck.check_leaderboard_settings(guild_id = interaction.guild.id)[5]:
            
            await interaction.response.edit_message(GetEmbed.get_embed(embed_index=4), view=ContinueSetting())

        else:
            
            get_messages = DatabaseCheck.check_leaderboard_settings(guild_id = interaction.guild.id)
            DatabaseUpdates.manage_leaderboard(guild_id = interaction.guild.id, settings = "channel", channel_id = self.channel_id)

            for i, index in (get_messages[2], "daily"), (get_messages[3], "weekly"), (get_messages[4], "monthly"):
                
                if i != None:
                
                    leaderboard_channel = bot.get_channel(get_messages[5])
                    
                    msg = await leaderboard_channel.fetch_message(i)
                    await msg.delete()

                    DatabaseUpdates.manage_leaderboard(guild_id = interaction.guild.id, back_to_none = index)

            emb = discord.Embed(description=f"""## Leaderboard channel has been overwritten
                {Emojis.dot_emoji} As of now, <#{self.channel_id}> is the new leaderboard channel
                {Emojis.dot_emoji} The leaderboard is deleted from the old leaderboard channel
                {Emojis.dot_emoji} You can continue with the setting using the selection menu below
                {Emojis.help_emoji} You can select several intervals and each interval is a single leaderboard""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=Setleaderboard())
        

    @discord.ui.button(
        label="keep current channel",
        style=discord.ButtonStyle.blurple,
        custom_id="keep_channel"
    )

    async def keep_channel(self, button, interaction:discord.Interaction):

        emb = discord.Embed(description=f"""## Channel is retained
            {Emojis.dot_emoji} The channel <#{DatabaseCheck.check_leaderboard_settings(guild_id = interaction.guild.id)[5]}> will be retained as a leaderboard channel
            {Emojis.dot_emoji} You can continue with the setting using the selection menu below
            {Emojis.help_emoji} You can select several intervals and each interval is a single leaderboard""", color=bot_colour)
        await interaction.response.edit_message(embed=emb, view=Setleaderboard())


class ContinueSetting(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="continue settings",
        style=discord.ButtonStyle.blurple,
        custom_id="continue_setting"
    )

    async def continue_setting_button(self, button, interaction:discord.Interaction):

        emb = discord.Embed(description=f"""## Set intervals
            {Emojis.dot_emoji} With the lower select menu you can define an interval in which periods the message leaderboard should be updated
            {Emojis.dot_emoji} You can also select several intervals, but you only need to select at least one
            {Emojis.help_emoji} As soon as you have selected the intervals, the leaderboards are sent to the channel you have previously set up and then always updated in the corresponding time periods""", color=bot_colour)
        await interaction.response.edit_message(embed=emb, view=Setleaderboard())


class LeaderboardOnOffSwitch(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label = "on / off switch",
            style = discord.ButtonStyle.blurple,
            custom_id = "on_off_switch"
        )

    async def callback(self, interaction:discord.Interaction):
        
        settings = DatabaseCheck.check_leaderboard_settings(guild_id = interaction.guild.id)
        DatabaseUpdates.manage_leaderboard(guild_id = interaction.guild.id, settings = "status")

        emb = discord.Embed(description=f"""## The message leaderboard system is now {'activated' if settings[1] == 0 else 'deactivated'}.
            {Emojis.dot_emoji} {f'''From now on all messages will be added to the message leaderboard and a ranking will be created showing who has written the most messages
            {Emojis.help_emoji} However, an interval and a channel must also be defined for this'''
            if settings[1] == 0 else f'''From now on, no messages will be added to the message leaderboard and the ranking will no longer be updated when you activate it again, the leaderboard will be reset and counted from the new interval.
            {Emojis.dot_emoji} The other settings remain as they are'''}""", color=bot_colour)
        await interaction.response.edit_message(embed=emb, view=None)


