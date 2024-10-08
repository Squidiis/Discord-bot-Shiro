
from cogs.level_system import *
from cogs.mod_tools import *
from dotenv import load_dotenv
from cogs.fun_commands import *
from utils import *
from cogs.leaderboard_system import *
from cogs.auto_react import *
import logging


@bot.command()
async def test(ctx):
    await ctx.send(f"Pong! Latency is ``{round(bot.latency*1000)}`` ms")

logging.basicConfig(level=logging.INFO)


class Main(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    # Creates all important tables for the bot 
    async def create_db_table():

        db_connect = await DatabaseSetup.db_connector()
        cursor = await db_connect.cursor()

        tables = [
            # Level system tables
            '''
            CREATE TABLE IF NOT EXISTS `LevelSystemStats` (
                guildId BIGINT UNSIGNED NOT NULL, 
                userId BIGINT UNSIGNED NOT NULL,
                userLevel BIGINT UNSIGNED NOT NULL,
                userXp BIGINT UNSIGNED NOT NULL,
                userName VARCHAR(255) NOT NULL,
                voiceTime TIMESTAMP(6) NULL,
                wholeXp BIGINT UNSIGNED NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            ''',
            '''
            CREATE TABLE IF NOT EXISTS LevelSystemBlacklist (
                guildId BIGINT UNSIGNED NOT NULL,
                channelId BIGINT UNSIGNED NULL,
                categoryId BIGINT UNSIGNED NULL,
                roleId BIGINT UNSIGNED NULL,
                userId BIGINT UNSIGNED NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            ''',
            '''
            CREATE TABLE IF NOT EXISTS LevelSystemRoles (
                guildId BIGINT UNSIGNED NOT NULL,
                roleId BIGINT UNSIGNED NOT NULL,
                roleLevel INT UNSIGNED NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            ''',
            '''
            CREATE TABLE IF NOT EXISTS LevelSystemSettings (
                guildId BIGINT UNSIGNED NOT NULL,
                xpRate INT UNSIGNED DEFAULT 20,
                levelStatus INT DEFAULT 0,
                levelUpChannel BIGINT UNSIGNED NULL,
                levelUpMessage VARCHAR(500) DEFAULT 'Oh nice {user} you have a new level, your newlevel is {level}',
                bonusXpPercentage INT UNSIGNED DEFAULT 10
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            ''',
            '''
            CREATE TABLE IF NOT EXISTS BonusXpList (
                guildId BIGINT UNSIGNED NOT NULL,
                channelId BIGINT UNSIGNED NULL,
                categoryId BIGINT UNSIGNED NULL,
                roleId BIGINT UNSIGNED NULL,
                userId BIGINT UNSIGNED NULL,
                PercentBonusXp INT UNSIGNED DEFAULT 0
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            ''',
            # Anti-link system table
            '''
            CREATE TABLE If NOT EXISTS AntiLinkWhiteList (
                guildId BIGINT UNSIGNED NOT NULL,
                channelId BIGINT UNSIGNED NULL,
                categoryId BIGINT UNSIGNED NULL,
                roleId BIGINT UNSIGNED NULL,
                userId BIGINT UNSIGNED NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            ''',
            # Bot settings table
            '''
            CREATE TABLE IF NOT EXISTS BotSettings (
                guildId BIGINT UNSIGNED NOT NULL,
                botColour VARCHAR(20) NULL,
                ghostPing INT DEFAULT 0,
                antiLink INT DEFAULT 3,
                antiLinkTimeout INT DEFAULT 0,
                autoReaction INT DEFAULT 0
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            ''',
            # Leaderboard tables
            '''
            CREATE TABLE IF NOT EXISTS LeaderboardSettingsMessage (
                guildId BIGINT UNSIGNED NOT NULL,
                statusMessage INT UNSIGNED NOT NULL DEFAULT 0,
                bourdMessageIdDay BIGINT UNSIGNED NULL,
                bourdMessageIdWeek BIGINT UNSIGNED NULL,
                bourdMessageIdMonth BIGINT UNSIGNED NULL,
                bourdMessageIdWhole BIGINT UNSIGNED NULL,
                leaderboardChannel BIGINT UNSIGNED NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            ''',
            '''
            CREATE TABLE IF NOT EXISTS LeaderboardTacking (
                guildId BIGINT UNSIGNED NOT NULL,
                userId BIGINT UNSIGNED NOT NULL,
                dailyCountMessage INT UNSIGNED DEFAULT 0,
                weeklyCountMessage INT UNSIGNED DEFAULT 0,
                monthlyCountMessage INT UNSIGNED DEFAULT 0,
                wholeCountMessage INT UNSIGNED DEFAULT 0,
                weeklyCountInvite INT UNSIGNED DEFAULT 0,
                monthlyCountInvite INT UNSIGNED DEFAULT 0,
                quarterlyCountInvite INT UNSIGNED DEFAULT 0,
                wholeCountInvite INT UNSIGNED DEFAULT 0
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            ''',
            '''
            CREATE TABLE IF NOT EXISTS LeaderboardRoles (
                guildId BIGINT UNSIGNED NOT NULL,
                roleId BIGINT UNSIGNED NOT NULL,
                rankingPosition INT UNSIGNED NOT NULL,
                status VARCHAR(20) NOT NULL,
                roleInterval VARCHAR(10) NOT NUll
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            ''',
            '''
            CREATE TABLE IF NOT EXISTS LeaderboardGivenRoles (
                guildId BIGINT UNSIGNED NOT NULL,
                roleId BIGINT UNSIGNED NOT NULL,
                userId BIGINT UNSIGNED NOT NULL,
                roleInterval VARCHAR(10) NOT NULL,
                status VARCHAR(20) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            ''',
            '''
            CREATE TABLE IF NOT EXISTS LeaderboardSettingsInvite (
                guildId BIGINT UNSIGNED NOT NULL,
                statusInvite INT UNSIGNED NOT NULL DEFAULT 0,
                invitebourdMessageIdWeek BIGINT UNSIGNED NULL,
                invitebourdMessageIdMonth BIGINT UNSIGNED NULL,
                invitebourdMessageIdQuarter BIGINT UNSIGNED NULL,
                invitebourdMessageIdWhole BIGINT UNSIGNED NULL,
                leaderboardChannel BIGINT UNSIGNED NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;  
            ''',
            '''
            CREATE TABLE IF NOT EXISTS LeaderboardInviteTracking (
                guildId BIGINT UNSIGNED NOT NULL,
                userId BIGINT UNSIGNED NOT NULL,
                inviteCode VARCHAR(20) NOT NULL,
                usesCount INT NOT NULL,
                UNIQUE KEY unique_invite (guildId, inviteCode)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            ''',
            # Auto reaction table
            '''
            CREATE TABLE IF NOT EXISTS AutoReactions (
                guildId BIGINT UNSIGNED NOT NULL,
                channelId BIGINT UNSIGNED NULL,
                categoryId BIGINT UNSIGNED NULL,
                parameter VARCHAR(255) NOT NULL,
                emoji VARCHAR(255) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            '''
            ]

        try:

            for table in tables:
                await cursor.execute(table)
                await db_connect.commit()
        
        except aiomysql.Error as error:
            print("parameterized query failed {}".format(error))


    @commands.Cog.listener()
    async def on_ready(self):

        view = View(timeout=None)
        print(f'Logged in as: {bot.user.name}')
        print(f'With ID: {bot.user.id}')

        print("┏━━━┓ ┏━━━┓ ┏┓ ┏┓ ┏━━┓ ┏━━━┓ ┏━━┓")
        print("┃┏━┓┃ ┃┏━┓┃ ┃┃ ┃┃ ┗┫┣┛ ┗┓┏┓┃ ┗┫┣┛")
        print("┃┗━━┓ ┃┃ ┃┃ ┃┃ ┃┃  ┃┃   ┃┃┃┃  ┃┃")
        print("┗━━┓┃ ┃┗━┛┃ ┃┃ ┃┃  ┃┃   ┃┃┃┃  ┃┃")
        print("┃┗━┛┃ ┗━━┓┃ ┃┗━┛┃ ┏┫┣┓ ┏┛┗┛┃ ┏┫┣┓")
        print("┗━━━┛    ┗┛ ┗━━━┛ ┗━━┛ ┗━━━┛ ┗━━┛")

        # level system
        self.bot.add_view(LevelRolesButtons(role_id=None, role_level=None, status=None))
        self.bot.add_view(ResetLevelStatsButton())

        # Level system settings
        self.bot.add_view(LevelSystemSetting())
        self.bot.add_view(SetLevelUpChannelSelect())
        self.bot.add_view(BonusXpPercentage())
        self.bot.add_view(SetXpRate())
        self.bot.add_view(LevelSystemDefault())
        self.bot.add_view(ShowLevelSettingsSelect())
        view.add_item(LevelUpMessageButton())
        view.add_item(SetLevelUpChannelButton())
        view.add_item(LevelSystemOnOffSwitch())
        view.add_item(SetBonusXpPercentageButton())
        view.add_item(SendXpBonusModal())
        view.add_item(ShowLevelSettings())

        # Mod tools
        self.bot.add_view(GhostPingButtons())

        # Message leaderboard
        self.bot.add_view(SetleaderboardChannel())
        self.bot.add_view(SetMessageleaderboard())
        self.bot.add_view(OverwriteMessageChannel(channel_id=None))
        self.bot.add_view(ContinueSettingLeaderboard())
        self.bot.add_view(OverwriteInterval(intervals=None))
        self.bot.add_view(OverwriteRole(role=None, interval=None, position=None, settings=None, delete=None))
        self.bot.add_view(ShowLeaderboardRolesButton())
        self.bot.add_view(ShowLeaderboardRolesSelectMessage())
        self.bot.add_view(ShowLeaderboardRolesSelectInvite())
        view.add_item(LeaderboardOnOffSwitch())
        view.add_item(DefaultSettingsLeaderboard())
        self.bot.add_view(ShowLeaderboardGivenRoles())
        self.bot.add_view(SetInviteleaderboard())

        # Auto-reaction
        self.bot.add_view(AutoReactionOnOffSwitch())
        self.bot.add_view(ShowAutoReactions())

        # Other Systems
        self.bot.add_view(RPSButtons(game_mode=None, second_user=None, first_user=None))

        self.bot.add_view(HelpMenuSelect())
        view.add_item(CancelButton(system=None))
        
        self.bot.add_view(view)
        await Main.create_db_table()
        await LeaderboardSystem.check_expired_invites()


    @commands.slash_command(description="Shows you the ping.")
    async def ping(self, ctx):
        await ctx.respond(f"Pong! Latency is ``{round(bot.latency*1000)}`` ms")


    @commands.Cog.listener()
    async def on_error(event, *args, **kwargs):
        logging.error(f"An error occurred in event {event}: {args} {kwargs}", exc_info=True)

    
    @commands.Cog.listener()
    async def on_guild_join(guild):

        await DatabaseUpdates._create_bot_settings(guild_id=guild.id)


logging.basicConfig(level=logging.INFO, filename='bot_errors.log', filemode='w',
    format='%(asctime)s - %(levelname)s - %(message)s')

def handle_exception(loop, context):
    msg = context.get("exception", context["message"])
    logging.error(f"Caught exception: {msg}")
    print(f"Caught exception: {msg}")

loop = asyncio.get_event_loop()
loop.set_exception_handler(handle_exception)



def load_cogs():

    for filename in os.listdir("cogs"):

        if filename.endswith(".py"):

            cog_name = f"cogs.{filename[:-3]}"

            try:

                bot.load_extension(cog_name)
                print(f"Loaded {cog_name}")

            except Exception as e:

                print(f"Failed to load {cog_name}: {e}")

bot.add_cog(Main(bot))


if __name__ == "__main__":

    try:

        load_dotenv()
        load_cogs()
        bot.run(os.getenv("TOKEN"))

    except Exception as e:

        logging.error(f"Bot crashed with error: {e}")

