import os
import mysql.connector

import discord
from discord.ext import commands


#######################  Database connection  #######################

'''
Establishes a connection to the db
All required data must be included in the .env file
'''
class DatabaseSetup():

    def db_connector():

        db_connector = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv("sql_password"), database=os.getenv('discord_db'), buffered=True)
        return db_connector

    def db_close(cursor, db_connection):

        if db_connection.is_connected():
            
            db_connection.close()
            cursor.close()

        else:
            pass

        

# Contains all important check functions for the level system 
class DatabaseStatusCheck():

    # Returns True if an element is on the blacklist.
    def _blacklist_check_text(guild_id:int, message_check:discord.Message):

        if isinstance(message_check.channel, discord.TextChannel):

            levelsystem_blacklist = DatabaseCheck.check_blacklist(guild_id=guild_id)

            if levelsystem_blacklist:

                for _, channel_blacklist, category_blacklist, role_blacklist, user_blacklist in levelsystem_blacklist:
                   
                    if user_blacklist == message_check.author.id:
                        return True

                    if role_blacklist != None:
                        
                        blacklist_role = message_check.guild.get_role(role_blacklist)
                        if blacklist_role in message_check.author.roles:
                            return True
                                
                    if message_check.channel.category_id == category_blacklist:
                        return True

                    if message_check.channel.id == channel_blacklist:
                        return True
                        
            else:
                return None
            
    
    # Returns the value True if "on" in the database and False when not
    def _level_system_status(guild_id:int):

        levelsystem_status = DatabaseCheck.check_level_settings(guild_id=guild_id)
        # Anpassen das es auch überprüft ob voice und so an ist!
        if levelsystem_status:

            if levelsystem_status[2] == "on":
                return True
            
            else:
                return False
            
        else:
            return None



##################################################  Database Statemants  #####################################

# Contains all check functions of the entire bot
class DatabaseCheck():

#################################################  Checks Level System  ##############################################################

    
    '''
    Checks whether a channel, category, role or user is on the blacklist
    '''
    def check_blacklist(
        guild_id:int, 
        channel_id:int = None, 
        category_id:int = None, 
        role_id:int = None, 
        user_id:int = None
        ):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()
        
        column_name = ["channelId", "categoryId", "roleId", "userId"]
        
        all_items = [channel_id, category_id, role_id, user_id]
        
        if all(x is None for x in all_items):
            
            check_blacklist = f"SELECT * FROM LevelSystemBlacklist WHERE guildId = %s"
            check_blacklist_values = [guild_id]

        else:
            
            for count in range(len(all_items)):
                if all_items[count] != None:
                    
                    check_blacklist = f"SELECT * FROM LevelSystemBlacklist WHERE guildId = %s AND {column_name[count]} = %s"
                    check_blacklist_values = [guild_id, all_items[count]]

        cursor.execute(check_blacklist, check_blacklist_values)
        
        if all(x is None for x in all_items):
            blacklist = cursor.fetchall()
        
        else:
            blacklist = cursor.fetchone()
            
        DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)
        return blacklist
 
    
    '''
    If you specify a user, the user's statistics are returned; if no user is specified, the statistics of all users on the server are returned
    Info:
        - The guild_id must be specified
    '''
    def check_level_system_stats(guild_id:int, user:int = None):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        if user != None:

            levelsys_stats_check = "SELECT * FROM LevelSystemStats WHERE guildId = %s AND userId = %s"
            levelsys_stats_check_values = [guild_id, user]

        else:

            levelsys_stats_check = "SELECT * FROM LevelSystemStats WHERE guildId = %s"
            levelsys_stats_check_values = [guild_id]

        cursor.execute(levelsys_stats_check, levelsys_stats_check_values)

        if user != None:
            levelsys_stats = cursor.fetchone()
        else:
            levelsys_stats = cursor.fetchall()

        DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)
        return levelsys_stats
    
    
    '''
    Returns all level roles that are available on the server

    Parameters:
    ------------
        - guild_id
            Id of the server
        - level_role
            The id of the level role to be returned
        - needed_level
            The level from which the role is assigned
        - status
            - check
                Checks whether the level or role is in the database
            - level_role
                Returns all level roles from level descending

    Info:
        - guild_id must be specified
        - If no status, level or role is specified, all level roles are returned
        - If a level is specified but no status or role, the entry for the level is returned
        - If only one role is specified and no level or status, the entry with the role is returned
        - If no entry exists, None is returned
    '''
    def check_level_system_levelroles(
        guild_id:int, 
        level_role:int = None, 
        needed_level:int = None, 
        status:str = None):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        if level_role != None and needed_level != None and status == None:

            levelsys_levelroles_check = "SELECT * FROM LevelSystemRoles WHERE guildId = %s AND roleId = %s AND roleLevel = %s"
            levelsys_levelroles_check_values = [guild_id, level_role, needed_level]
        
        elif level_role != None and needed_level == None and status == None:

            levelsys_levelroles_check = "SELECT * FROM LevelSystemRoles WHERE guildId = %s AND roleId = %s"
            levelsys_levelroles_check_values = [guild_id, level_role]

        elif level_role == None and needed_level != None and status == None:

            levelsys_levelroles_check = "SELECT * FROM LevelSystemRoles WHERE guildId = %s AND roleLevel = %s"
            levelsys_levelroles_check_values = [guild_id, needed_level]

        elif level_role != None and needed_level != None and status == "check":

            levelsys_levelroles_check = "SELECT * FROM LevelSystemRoles WHERE guildId = %s AND roleId = %s OR roleLevel = %s"
            levelsys_levelroles_check_values = [guild_id, level_role, needed_level]

        elif level_role == None and needed_level == None and status == "level_role":
            
            levelsys_levelroles_check = "SELECT * FROM LevelSystemRoles WHERE guildId = %s ORDER BY roleLevel DESC"
            levelsys_levelroles_check_values = [guild_id]

        else:

            levelsys_levelroles_check = "SELECT * FROM LevelSystemRoles WHERE guildId = %s"
            levelsys_levelroles_check_values = [guild_id]

        cursor.execute(levelsys_levelroles_check, levelsys_levelroles_check_values)

        if level_role == None and needed_level == None:
            levelsys_levelroles = cursor.fetchall()
        else:
            levelsys_levelroles = cursor.fetchone()

        DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)
        return levelsys_levelroles
    

    '''
    Returns the entries of the bonus-xp-list that are defined for a server, 
    if you specify individual IDs, the system only checks whether they are present, if they are not present, none is returned if they are present, the entire entry is returned 

    Parameters:
    -----------
        - guild_id
            Id of the server
        - channel_id
            Id of the channel to be checked
        - category_id
            Id of the category to be checked
        - role_id 
            Id of the role to be checked
        - user_id
            Id of the user to be checked

    Info:
        - guild_id must be specified
        - If only the `guild_id` is specified, all entries specified for the server are returned
        - Always specify only one id otherwise errors may occur     
    '''
    def check_xp_bonus_list(
        guild_id:int, 
        channel_id:int = None, 
        category_id:int = None, 
        role_id:int = None, 
        user_id:int = None
        ):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()
        
        column_name = ["channelId", "categoryId", "roleId", "userId"]
        
        all_items = [channel_id, category_id, role_id, user_id]
        
        if all(x is None for x in all_items):
            
            check_xp_bonus_list = f"SELECT * FROM BonusXpList WHERE guildId = %s"
            check_xp_bonus_list_values = [guild_id]

        else:
            
            for count in range(len(all_items)):
                if all_items[count] != None:
                    
                    check_xp_bonus_list = f"SELECT * FROM BonusXpList WHERE guildId = %s AND {column_name[count]} = %s"
                    check_xp_bonus_list_values = [guild_id, all_items[count]]

        cursor.execute(check_xp_bonus_list, check_xp_bonus_list_values)
        
        if all(x is None for x in all_items):
            xp_bonus_list = cursor.fetchall()
        
        else:
            xp_bonus_list = cursor.fetchone()
            
        DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)
        return xp_bonus_list
    

    '''
    Returns the settings of a server if you enter the guild_id
    '''
    def check_level_settings(guild_id:int):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        level_settings_check = "SELECT * FROM LevelSystemSettings WHERE guildId = %s"
        level_settings_check_values = [guild_id]
        cursor.execute(level_settings_check, level_settings_check_values)
        level_system_settings = cursor.fetchone()

        DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)
        return level_system_settings
    

    '''
    Returns either all entries of the antilink whitelist or only specific ones depending on which item is specified

    Parameters:
    -----------
        - guild_id
            Id of the server
        - channel_id
            Id of the channel to be checked
        - category_id
            Id of the category to be checked
        - role_id
            Id of the role to be checked
        - user_id
            Id of the user to be checked
    
    Info:
        - guild_id must be specified
        - Depending on which item you specify, you will receive the respective entries from the database
        - If you do not specify a channel, category, role or user id, the entire whitelist will be returned
    '''
    def check_antilink_whitelist(
        guild_id:int, 
        channel_id:int = None, 
        category_id:int = None, 
        role_id:int = None, 
        user_id:int = None
        ):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        column_name = ["channelId", "categoryId", "roleId", "userId"]
        
        all_items = [channel_id, category_id, role_id, user_id]
        
        if all(x is None for x in all_items):
            
            check_white_list = f"SELECT * FROM AntiLinkWhiteList WHERE guildId = %s"
            check_white_list_values = [guild_id]

        else:
            
            for count in range(len(all_items)):
                if all_items[count] != None:
                    
                    check_white_list = f"SELECT * FROM AntiLinkWhiteList WHERE guildId = %s AND {column_name[count]} = %s"
                    check_white_list_values = [guild_id, all_items[count]]

        cursor.execute(check_white_list, check_white_list_values)
        
        if all(x is None for x in all_items):
            white_list = cursor.fetchall()
        
        else:
            white_list = cursor.fetchone()
            
        DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)
        return white_list





########################################################  Checks the bot settings  ##############################################


    '''
    Returns how the level system is set on the respective servers

    Info:
        - guild_id must be specified
    '''
    def check_bot_settings(guild_id:int):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        bot_settings_check = "SELECT * FROM BotSettings WHERE guildId = %s"
        bot_settings_check_values = [guild_id]
        cursor.execute(bot_settings_check, bot_settings_check_values)
        bot_settings = cursor.fetchone()

        DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)
        return bot_settings
    




#####################################  Inserting and updating the database  ####################################

class DatabaseUpdates():

###############################################  Bot Settings  ###############################################

    '''
    Creates entries for a server on which the bot has just joined

    Table Daten: 

        BotSettings:
            guildId BIGINT UNSIGNED NOT NULL
            botColour VARCHAR(20) NULL
            ghostPing BIT DEFAULT 0
            antiLink BIT(4) DEFAULT 3
            antiLinkTimeout INT DEFAULT 0

        LevelSystemSettings:
            guildId BIGINT UNSIGNED NOT NULL,
            xpRate INT UNSIGNED DEFAULT 20,
            levelStatus VARCHAR(50) DEFAULT 'on',
            levelUpChannel BIGINT UNSIGNED NULL,
            levelUpMessage VARCHAR(500) DEFAULT 'Oh nice {user} you have a new level, your newlevel is {level}',
            bonusXpPercentage INT UNSIGNED DEFAULT 10
    '''
    def _create_bot_settings(guild_id:int):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        sql_tables = ["BotSettings", "LevelSystemSettings"]

        try:

            for table in sql_tables:

                creat_bot_settings = f"INSERT INTO {table} (guildId) VALUES (%s)"
                creat_bot_settings_values = [guild_id]
                cursor.execute(creat_bot_settings, creat_bot_settings_values)
                db_connect.commit()

        except mysql.connector.Error as error:
           print("parameterized query failed {}".format(error))

        finally:

            DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)


    '''
    Updates the individual settings of the bot

    Parameters:
    -----------
        - guild_id
            The server id of the current server
        - bot_colour
            The color code which color the embeds should have (can also be changed in config.yaml)
        - ghost_ping
            How the ghost_ping system should work
                - 1: switched on
                - 0: switched off
        - antilink
            How the antilink system should behave
                - 0: All messages with a discord invitation link will be deleted
                - 1: Every message with a link will be deleted exept Pictures and Videos
                - 2: All messages with a link will be deleted this also includes pictures and videos
                - 3: Deactivate antilink system! (no messages are deleted)
        - antilink_timeout
            How long someone should receive a timeout if they violate the antilink system
        - back_to_none
            Depending on the value, a system is set back to default settings
                - 0: The bot color is set back to the default value
                - 1: The ghost ping system is switched off
                - 2: The Antilink system is switched off
                - 3: The Antilink timeout is set back to 0 minutes 

    Info:
        - guild_id must be specified
        - all values must have the specified data type
    '''
    def update_bot_settings(
        guild_id:int, 
        bot_colour:str = None, 
        ghost_ping:int = None, 
        antilink:int = None, 
        antilink_timeout:int = None,
        back_to_none:int = None
        ):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()
        
        column_name = ["botColour", "ghostPing", "antiLink", "antiLinkTimeout"]
        items = [bot_colour, ghost_ping, antilink]

        try:
            
            if back_to_none == None:

                for count in range(len(items)):
                    
                    if items[count] != None:

                        update_settings = f'UPDATE BotSettings SET {column_name[count]} = %s{f", antiLinkTimeout = {antilink_timeout}" if antilink_timeout != None else ""} WHERE guildId = %s'
                        update_settings_values = (items[count], guild_id)
                        cursor.execute(update_settings, update_settings_values)
                        db_connect.commit()

            else:

                update_settings = f'UPDATE BotSettings SET {column_name[back_to_none]} = DEFAULT WHERE guildId = %s'
                update_settings_values = [guild_id]
                cursor.execute(update_settings, update_settings_values)
                db_connect.commit()
            
        except mysql.connector.Error as error:
            print('parameterized query failed {}'.format(error))

        finally:

            DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)


    '''
    Serves to set the antilink whitelist, can add as well as remove or completely reset things

    Parameters:
    -----------
        - guild_id
            Id of the server
        - operation
            What should be done
                - add: If something is to be added to the whitelist
                - remove: If something is to be removed from the whitelist
                - reset: Resets the whitelist
        - channel_id
            Id of the channel you want to add or remove
        - category_id
            Id of the category you want to add or remove
        - role_id
            Id of the role you want to add or remove
        - user_id
            Id of the user you want to add or remove

    Info:
        - guild_id must be specified
        - An operation must be specified either add, remove or reset
    '''
    def manage_antilink_whitelist(
        guild_id:int, 
        operation:str, 
        channel_id:int = None, 
        category_id:int = None, 
        role_id:int = None, 
        user_id:int = None
        ):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()
        
        column_name = ["channelId", "categoryId", "roleId", "userId"]
        items = [channel_id, category_id, role_id, user_id]
        
        try:
            
            if any(elem is not None for elem in items) and operation != "reset":

                for count in range(len(items)):
                    
                    if items[count] != None:
                        
                        if operation == "add":
                            
                            white_list = f"INSERT INTO AntiLinkWhiteList (guildId, {column_name[count]}) VALUES (%s, %s)"
                            white_list_values = [guild_id, items[count]]
                        
                        elif operation == "remove":
                            
                            white_list = f"DELETE FROM AntiLinkWhiteList WHERE guildId = %s AND {column_name[count]} = %s"
                            white_list_values = [guild_id, items[count]]

                        cursor.execute(white_list, white_list_values)
                        db_connect.commit()

            elif operation == "reset":
                
                white_list = f"DELETE FROM AntiLinkWhiteList WHERE guildId = %s"
                white_list_values = [guild_id]

                cursor.execute(white_list, white_list_values)
                db_connect.commit()

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)



########################################  Insert into / Update the Level System  ##################################################


    '''
    Creates entries for users who are new to the level system 

    Parameters:
    -----------
        - guild_id
            Id of the server
        - user_id
            Id of the user
        - user_name
            Name of the user
        - user_level
            Number of levels the user has (is always 0 at the beginning)
        - user_xp
            Number of XP the user has (is always 0 at the beginning)
        - whole_xp
            Number of XP the user has in total (is always 0 at the beginning)

    Info:
        - guild_id, user_id, user_level must be specified
        - All other values have a default value and do not need to be changed
    '''
    def _insert_user_stats_level(
        guild_id:int, 
        user_id:int, 
        user_name:str, 
        user_level:int = 0, 
        user_xp:int = 0, 
        whole_xp:int = 0
        ):
    
        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        try:

            insert_new_user = "INSERT INTO LevelSystemStats (guildId, userId, userLevel, userXp, userName, wholeXp) VALUES (%s, %s, %s, %s, %s, %s)"        
            insert_new_user_values = [guild_id, user_id, user_level, user_xp, user_name, whole_xp]
            cursor.execute(insert_new_user, insert_new_user_values)
            db_connect.commit()

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)
    

    '''
    Creates entries for the level roles

    Parameters:
    -----------
        - guild_id
            Id of the server
        - role_id
            Id of the new level role
        - level
            Level from which the level role should be assigned
        - guild_name
            Name of the server
    
    Info:
        - All values must be specified
    '''
    def _insert_level_roles(
        guild_id:int, 
        role_id:int, 
        level:int, 
        guild_name:str):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        try:

            insert_level_role = "INSERT INTO LevelSystemRoles (guildId, roleId, roleLevel, guildName) VALUES (%s, %s, %s, %s)"
            insert_level_role_values = [guild_id, role_id, level, guild_name]
            cursor.execute(insert_level_role, insert_level_role_values)
            db_connect.commit()

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)
        

    '''
    Serves to set the level system blacklist, can add as well as remove or completely reset things

    Parameters:
    -----------
        - guild_id
            Id of the server
        - operation
            What should be done
                - add: If something is to be added to the blacklist
                - remove: If something is to be removed from the blacklist
                - reset: Resets the blacklist
        - channel_id
            Id of the channel you want to add or remove
        - category_id
            Id of the category you want to add or remove
        - role_id
            Id of the role you want to add or remove
        - user_id
            Id of the user you want to add or remove

    Info:
        - guild_id must be specified
        - An operation must be specified either add, remove or reset
    '''
    def manage_blacklist(
        guild_id:int, 
        operation:str, 
        channel_id:int = None, 
        category_id:int = None, 
        role_id:int = None, 
        user_id:int = None
        ):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()
        
        column_name = ["channelId", "categoryId", "roleId", "userId"]
        items = [channel_id, category_id, role_id, user_id]
        
        try:
            
            if any(i is not None for i in items) and operation != "reset":
            
                for count in range(len(items)):
                    
                    if items[count] != None:

                        if operation == "add":
                            
                            level_sys_blacklist = f"INSERT INTO LevelSystemBlacklist (guildId, {column_name[count]}) VALUES (%s, %s)"
                            level_sys_blacklist_values = [guild_id, items[count]]
                        
                        elif operation == "remove":
                            
                            level_sys_blacklist = f"DELETE FROM LevelSystemBlacklist WHERE guildId = %s AND {column_name[count]} = %s"
                            level_sys_blacklist_values = [guild_id, items[count]]

                        cursor.execute(level_sys_blacklist, level_sys_blacklist_values)
                        db_connect.commit()

            elif operation == "reset":
                
                level_sys_blacklist = f"DELETE FROM LevelSystemBlacklist WHERE guildId = %s"
                level_sys_blacklist_values = [guild_id]
        
                cursor.execute(level_sys_blacklist, level_sys_blacklist_values)
                db_connect.commit()

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)

    
    '''
    Updates the individual settings of the level system

    Parameters:
    -----------
        - guild_id
            The server id of the current server
        - xp_rate
            Amount of XP awarded per message
        - level_status
            - on
            - off
        - level_up_channel
            Channel in which level up notifications are sent
        - level_up_message
            Level up notification message
        - percentage
            Percentage of how much more XP should be awarded when writing to a channel, category, role or user
        - back_to_none
            Depending on the value, a system is set back to default settings
                - 0: xp rate is set back to 20
                - 1: The level system is set to `on
                - 2: Level up channel is reset so level up notifications are sent back to the channel with the last activity
                - 3: Level up message is set back to `Oh nice {user} you have a new level, your newlevel is {level}`
                - 4: The bonus XP percentage is set back to 10

    Info:
        - guild_id must be specified
        - all values must have the specified data type
    '''
    def update_level_settings(
        guild_id:int, 
        xp_rate:int = None, 
        level_status:str = None, 
        level_up_channel:int = None, 
        level_up_message:str = None, 
        percentage:int = None, 
        back_to_none:int = None
        ):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        column_name = ["xpRate", "levelStatus", "levelUpChannel", "levelUpMessage","bonusXpPercentage"]
        items = [xp_rate, level_status, level_up_channel, level_up_message, percentage]

        try:
            
            if back_to_none == None:

                for count in range(len(items)):

                    if items[count] != None:

                        update_settings = f"UPDATE LevelSystemSettings SET {column_name[count]} = %s WHERE guildId = %s"
                        update_settings_values = (items[count], guild_id)
                        cursor.execute(update_settings, update_settings_values)
                        db_connect.commit()

            else:

                update_settings = f"UPDATE LevelSystemSettings SET {column_name[back_to_none]} = DEFAULT WHERE guildId = %s"
                update_settings_values = [guild_id]
                cursor.execute(update_settings, update_settings_values)
                db_connect.commit()
            
        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)


    '''
    Updates the stats of a single user

    Parameters:
    -----------
        - guild_id
            Server id
        - user_id
            Id of the user whose stats are to be changed
        - level
            New level of the user
        - xp
            New amount of XP of the user
        - whole_xp
            Amount of the user's total XP

    Info:
        - guild_id and user_id must be specified as well as either XP and whole_xp or level
        - If you give a user XP without having earned it through activities, it will not be counted towards the whole_xp
    ''' 
    def _update_user_stats_level(
        guild_id:int, 
        user_id:int, 
        level:int = None, 
        xp:int = None, 
        whole_xp:int = None
        ):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        try:

            if xp != None and whole_xp != None:

                update_stats = f"UPDATE LevelSystemStats SET userXp = %s, wholeXp = %s WHERE guildId = %s AND userId = %s"
                update_stats_values = [xp, whole_xp, guild_id, user_id]

            elif xp != None and whole_xp == None:

                update_stats = f"UPDATE LevelSystemStats SET userXp = %s WHERE guildId = %s AND userId = %s"
                update_stats_values = [xp, guild_id, user_id]

            elif level != None:

                update_stats = f"UPDATE LevelSystemStats SET userLevel = %s, userXp = %s, wholeXp = %s WHERE guildId = %s AND userId = %s"
                update_stats_values = [level, 0, whole_xp, guild_id, user_id]
            
            cursor.execute(update_stats, update_stats_values)
            db_connect.commit()

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)


    '''
    Updates the level-roles

    Parameters:
    -----------
        - guild_id
            Id of the server
        - role_id
            Id of the role to be changed
        - role_level
            Level at which a role is to be redefined
        - status
            Which value is to be overwritten
                - role: The role is given a new level
                - level: The level receives a new role

    Info:
        - guild_id must be specified
        - status only needs to be specified if you want to overwrite an existing entry 
    '''
    def update_level_roles(
        guild_id:int, 
        role_id:int = None, 
        role_level:int = None, 
        status:str = None
        ):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor() 
     
        try:

            if status == "role":
                    
                update_level_roles = "UPDATE LevelSystemRoles SET roleLevel = %s WHERE guildId = %s AND roleId = %s"
                update_level_roles_values = [role_level, guild_id, role_id]
                
            elif status == "level":

                update_level_roles = "UPDATE LevelSystemRoles SET roleId = %s WHERE guildId = %s AND roleLevel = %s"
                update_level_roles_values = [role_id, guild_id, role_level]

            cursor.execute(update_level_roles, update_level_roles_values)
            db_connect.commit()

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)

    
    '''
    Serves to set the bonus xp list, can add as well as remove or completely reset things

    Parameters:
    -----------
        - guild_id
            Id of the server
        - operation
            What should be done
                - add: If something is to be added to the bonus xp list
                - remove: If something is to be removed from the bonus xp list
                - reset: Resets the bonus xp list
        - channel_id
            Id of the channel you want to add or remove
        - category_id
            Id of the category you want to add or remove
        - role_id
            Id of the role you want to add or remove
        - user_id
            Id of the user you want to add or remove

    Info:
        - guild_id must be specified
        - An operation must be specified either add, remove or reset
    '''
    def manage_xp_bonus(
        guild_id:int, 
        operation:str, 
        channel_id:int = None, 
        category_id:int = None, 
        role_id:int = None, 
        user_id:int = None, 
        bonus:int = None
        ):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()
        
        column_name = ["channelId", "categoryId", "roleId", "userId"]
        items = [channel_id, category_id, role_id, user_id]
        
        try:
            
            if any(elem is not None for elem in items) and operation != "reset":

                for count in range(len(items)):
                    
                    if items[count] != None:
                        
                        if operation == "add":
                            
                            bonus_list = f"INSERT INTO BonusXpList (guildId, {column_name[count]}) VALUES (%s, %s)" if bonus == None else f"INSERT INTO BonusXpList (guildId, {column_name[count]}, PercentBonusXp) VALUES (%s, %s, %s)"
                            bonus_list_values = [guild_id, items[count]] if bonus == None else [guild_id, items[count], bonus]
                        
                        elif operation == "remove":
                            
                            bonus_list = f"DELETE FROM BonusXpList WHERE guildId = %s AND {column_name[count]} = %s"
                            bonus_list_values = [guild_id, items[count]]

                        cursor.execute(bonus_list, bonus_list_values)
                        db_connect.commit()

            elif operation == "reset":
                
                bonus_list = f"DELETE FROM BonusXpList WHERE guildId = %s"
                bonus_list_values = [guild_id]

                cursor.execute(bonus_list, bonus_list_values)
                db_connect.commit()

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)





class DatabaseRemoveDatas():

###########################################################  Removes values from the level system  #######################################


    '''
    Deletes either the stats of a specific user or those of all users, depending on whether a user is specified

    Info:
        - guild_id must be specified
        - If no user_id is specified, all entries belonging to the server are deleted
    '''
    def _remove_level_system_stats(guild_id:int, user_id:int = None):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        try:
        
            remove_stats = "DELETE FROM LevelSystemStats WHERE guildId = %s AND userId = %s" if user_id != None else "DELETE FROM LevelSystemStats WHERE guildId = %s"
            remove_stats_values = [guild_id, user_id] if user_id != None else [guild_id]
            
            cursor.execute(remove_stats, remove_stats_values)
            db_connect.commit()

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            DatabaseSetup.db_close(db_connection=db_connect, cursor=cursor)


    '''
    Deletes level roles

    Parameters:
    -----------
        - guild_id
            Id of the server
        - role_id
            Id of the role to be deleted as level role
        - role_level
            Level of a role that is to be deleted as a level role

    Info:
        - guild_id must be specified
        - If no role_id or role_level is specified, all roles are removed as level roles
    '''
    def _remove_level_system_level_roles(guild_id:int, role_id:int = None, role_level:int = None):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        if role_id != None and role_level == None:
            column_name, data = "roleId", role_id
        elif role_level != None and role_id == None:
            column_name, data = "roleLevel", role_level

        try:

            if all(x is None for x in [role_id, role_level]):
                remove_level_role = "DELETE FROM LevelSystemRoles WHERE guildId = %s"
                remove_level_role_values = [guild_id]

            else:

                remove_level_role = f"DELETE FROM LevelSystemRoles WHERE guildId = %s AND {column_name} = %s"
                remove_level_role_values = [guild_id, data]

            cursor.execute(remove_level_role, remove_level_role_values)
            db_connect.commit()

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            DatabaseSetup.db_close(db_connection=db_connect, cursor=cursor)



