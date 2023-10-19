
"""
┏━━━┓ ┏━━━┓ ┏┓ ┏┓ ┏━━┓ ┏━━━┓ ┏━━┓
┃┏━┓┃ ┃┏━┓┃ ┃┃ ┃┃ ┗┫┣┛ ┗┓┏┓┃ ┗┫┣┛
┃┗━━┓ ┃┃ ┃┃ ┃┃ ┃┃  ┃┃   ┃┃┃┃  ┃┃
┗━━┓┃ ┃┗━┛┃ ┃┃ ┃┃  ┃┃   ┃┃┃┃  ┃┃
┃┗━┛┃ ┗━━┓┃ ┃┗━┛┃ ┏┫┣┓ ┏┛┗┛┃ ┏┫┣┓
┗━━━┛    ┗┛ ┗━━━┛ ┗━━┛ ┗━━━┛ ┗━━┛
"""

from datetime import * 
from discord import ButtonStyle, Interaction
import requests
from Import_file import * 
from typing import List



class RPSButtons(discord.ui.View):
    def __init__(self, game_mode, second_user, first_user):
        self.game_mode = game_mode
        self.second_user = second_user
        self.first_user = first_user
        super().__init__(timeout=None)
        self.check_useres = {"first_user":self.first_user.id, "second_user":self.second_user.id}
        self.user_choice = {"first_user_choice":"", "second_user_choice":""}
        self.false_user_emb = discord.Embed(title=f"{Emojis.help_emoji} Du kannst nicht an diesem Spiel Teilnehmen {Emojis.exclamation_mark_emoji}", 
            description=f"""{Emojis.dot_emoji} Du kannst hier nichts auswählen da du nicht zu dieser Partie eingeladen wurdest.""", color=bot_colour)
        self.wait_emb = discord.Embed(title=f"{Emojis.help_emoji} Warte nocht etwas", 
            description=f"""{Emojis.dot_emoji} Warte auf die antwort deines Spiel partners""", color=bot_colour)
    
    def rps_analysis(self):

        bot_choice = random.choice(["rock", "paper", "scissors"])
    
        win_emb = discord.Embed(title=f"{'Du hast gewonnen!' if self.game_mode == 0 else f'{self.first_user.name} hat gegen {self.second_user.name} gewonnen'}", 
            description=f"""{Emojis.dot_emoji} Deine wahl: {self.user_choice["first_user_choice"]}
            {Emojis.dot_emoji} {f'Die Wahl des bots: {bot_choice}' if self.user_choice["second_user_choice"] == None else f'Die wahl von {self.second_user.name}: {self.user_choice["second_user_choice"]}'}""", color=bot_colour)

        lose_emb = discord.Embed(title="Verloren")

        tie_emb = discord.Embed(title="Unentschieden!")

        results = {
        "rock": {"rock": tie_emb, "paper": lose_emb, "scissors": win_emb},
        "paper": {"rock": win_emb, "paper": tie_emb, "scissors": lose_emb},
        "scissors": {"rock": lose_emb, "paper": win_emb, "scissors": tie_emb}}

        return results[self.user_choice["first_user_choice"]][self.user_choice["second_user_choice"]] if self.game_mode == 1 else results[self.user_choice["first_user_choice"]][bot_choice]


    @discord.ui.button(label="rock", style=discord.ButtonStyle.blurple, custom_id="rock")
    async def rock_callback(self, button, interaction:discord.Interaction):

        if self.game_mode == 1:

            if interaction.user.id == self.second_user.id and self.check_useres["second_user"] == interaction.user.id:

                self.check_useres["second_user"], self.user_choice["second_user_choice"] = True, "rock"

                if self.user_choice["first_user_choice"] != "":

                    emb = self.rps_analysis()
                    await interaction.response.edit_message(embed=emb, view=None)

            elif interaction.user.id == self.second_user.id and self.check_useres["second_user"] == True:

                await interaction.response.send_message(embed=self.wait_emb, ephemeral=True)

            elif interaction.user.id == self.first_user.id and self.check_useres["first_user"] == interaction.user.id:

                self.check_useres["first_user"], self.user_choice["first_user_choice"] = True, "rock"

                if self.user_choice["second_user_choice"] != "":
                    
                    emb = self.rps_analysis()
                    await interaction.response.edit_message(embed=emb, view=None)

            elif interaction.user.id == self.first_user.id and self.check_useres["first_user"] == True:

                await interaction.response.send_message(embed=self.wait_emb, ephemeral=True)

            else:

                await interaction.response.send_message(embed=self.false_user_emb, ephemeral=True)
            
            
        else:

            emb = self.rps_analysis(choice_user="rock")
            await interaction.response.edit_message(embed=emb, view=None)

    @discord.ui.button(label="paper", style=discord.ButtonStyle.blurple, custom_id="paper")
    async def paper_callback(self, interaction:discord.Interaction, button):

        emb = self.rps_analysis()
        await interaction.response.edit_message(embed=emb, view=None)

    @discord.ui.button(label="scissors", style=discord.ButtonStyle.blurple, custom_id="scissors")
    async def scissors_callback(self, interaction:discord.Interaction, button):

        emb = self.rps_analysis()
        await interaction.response.edit_message(embed=emb, view=None)


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
      

    @commands.slash_command(name = "rps")
    async def rps(self, ctx:commands.Context, user:Option(discord.Member, description="Wähle einen user mit den herausfordern möchtest du kann auch gegen einen bot spielen") = None):

        if user == None or user.bot:

            emb = discord.Embed()
            await ctx.respond(embed=emb, view=RPSButtons(game_mode=0))

        else:

            emb = discord.Embed(title="Multi")
            await ctx.respond(embed=emb, view=RPSButtons(game_mode=1, second_user=user, first_user=ctx.author))


    @commands.command()
    async def coinflip(self, ctx):
        
        Tail = discord.File("assets/coin_flip/tail_coin.png", filename="tail_coin.png")
        Head = discord.File("assets/coin_flip/head_coin.png", filename="head_coin.png")
        emb = discord.Embed(title="", description=f"**{ctx.author.mention} has flipped the coin!**", color=discord.Colour.random())
        emb.set_image(url = "https://cdn.dribbble.com/users/1102039/screenshots/6574749/multi-coin-flip.gif")
        coin = [Tail, Head]
        coinsite = ""
        random_flip = random.choice(coin)
        
        if random_flip == Tail:
            coinsite = "Tale"

        elif random_flip == Head:
            coinsite = "Head"
        
        embed1 = await ctx.send(embed=emb)
        await asyncio.sleep(5)
        
        emb = discord.Embed(title=f"You flipped {coinsite}", description="", color=discord.Colour.random())
        emb.set_image(url=f"attachment://{random_flip}")
        await embed1.edit (embed=emb, file=random_flip)



    @commands.slash_command(description="Gives you a random cocktail recipe.")
    async def cocktails(self, ctx):
        cocktails = requests.get("https://www.thecocktaildb.com/api/json/v1/1/random.php").json()["drinks"][0]
        name = cocktails['strDrink']
        
        alcohol = cocktails['strAlcoholic']
        instructions = cocktails['strInstructions']
        ingredients = []
        
        for i in range(15):
            measure = cocktails.get(f"strMeasure{i}")
            ingredient = cocktails.get(f"strIngredient{i}")
            if ingredient is not None:
                ingredients.append(f'{ingredient} {measure}')

        allIngredients_string = ", ".join(ingredients)
        measures = []
        allmeasures_string = ", ".join(measures)

        Recipe = f"{allIngredients_string} {allmeasures_string}"
            
        if alcohol == "Alcoholic":
            Alcohol = "Yes"
        else:
            Alcohol = "No"
    
        DrinkThumb = cocktails['strDrinkThumb']
        
        emb = discord.Embed(title=f"Name: {name}", description=f"""
        Alcoholic: {Alcohol}
        
        Recipe: {Recipe} 

        Instructions: {instructions}
        
        """, color=discord.Colour.random())
        emb.set_image(url=DrinkThumb)
        await ctx.respond(embed=emb)

    

class TicTacToeButton(discord.ui.Button['TicTacToe']):
    def __init__(self, x: int, y: int):
        super().__init__(style=discord.ButtonStyle.secondary, label='\u200b', row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: TicTacToe = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            return

        if view.current_player == view.X:
            self.style = discord.ButtonStyle.danger
            self.label = 'X'
            self.disabled = True
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            content = "It is now O's turn"
        else:
            self.style = discord.ButtonStyle.success
            self.label = 'O'
            self.disabled = True
            view.board[self.y][self.x] = view.O
            view.current_player = view.X
            content = "It is now X's turn"

        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                content = 'X won!'
            elif winner == view.O:
                content = 'O won!'
            else:
                content = "It's a tie!"

            for child in view.children:
                child.disabled = True

            view.stop()

        await interaction.response.edit_message(content=content, view=view)

class TicTacToe(discord.ui.View):

    children: List[TicTacToeButton]
    X = -1
    O = 1
    Tie = 2

    def __init__(self):
        super().__init__()
        self.current_player = self.X
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]

        
        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))

    # This method checks for the board winner -- it is used by the TicTacToeButton
    def check_board_winner(self):
        for across in self.board:
            value = sum(across)
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check vertical
        for line in range(3):
            value = self.board[0][line] + self.board[1][line] + self.board[2][line]
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check diagonals
        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        # If we're here, we need to check if a tie was made
        if all(i != 0 for row in self.board for i in row):
            return self.Tie

        return None


class TicTacToeBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('?'))


bott = TicTacToeBot()

@bot.command()
async def tic(ctx: commands.Context):
    """Starts a tic-tac-toe game with yourself."""
    await ctx.send('Tic Tac Toe: X goes first', view=TicTacToe())



def setup(bot):
    bot.add_cog(Fun(bot))





