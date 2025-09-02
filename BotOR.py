import os
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Je suis vivant !"

@app.route('/healthz')
def healthz():
    return "OK", 200

def run():
  app.run(host='0.0.0.0', port=8080)

def keep_alive():  
    t = Thread(target=run)
    t.start()

# Assurez-vous d'appeler cette fonction avant de lancer le bot
# Ajoutez keep_alive() avant bot.run(bot_token)

# IMPORTANT : Le token est récupéré d'une variable d'environnement pour la sécurité
# Remplacez cette ligne par bot.run('VOTRE_TOKEN_ICI') si vous l'exécutez en local
bot_token = os.environ.get('DISCORD_TOKEN')

# On active les intents nécessaires pour lire les messages et gérer les membres
intents = discord.Intents.default()
intents.members = True
intents.message_content = True 

# On définit le préfixe de commande et les intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Dictionnaire de configuration pour personnaliser le message et les boutons
config = {
    'message': "Clique sur un bouton pour choisir ta plateforme",
    'roles': {
        "1404174466954821713": {"label": "PC", "style": discord.ButtonStyle.primary},
        "1404174313841758341": {"label": "Console", "style": discord.ButtonStyle.success},
        "1412064566539583633": {"label": "Membre", "style": discord.ButtonStyle.secondary}
    }
}

class MyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_buttons()

    def add_buttons(self):
        for role_id, role_data in config['roles'].items():
            button = discord.ui.Button(
                label=role_data['label'],
                style=role_data['style'],
                custom_id=role_id
            )
            button.callback = self.button_callback
            self.add_item(button)

    async def button_callback(self, interaction: discord.Interaction):
        role_id = int(interaction.data['custom_id'])
        guild = interaction.guild
        member = interaction.user
        role = guild.get_role(role_id)

        if role is not None:
            if role in member.roles:
                await member.remove_roles(role)
                await interaction.response.send_message(f"❌ Le rôle **{role.name}** t'a été retiré.", ephemeral=True)
            else:
                await member.add_roles(role)
                await interaction.response.send_message(f"✅ Le rôle **{role.name}** t'a été attribué.", ephemeral=True)
        else:
            await interaction.response.send_message("Ce rôle n'existe plus.", ephemeral=True)

@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user}')
    # Ajoute la vue au bot pour qu'elle continue de fonctionner même après un redémarrage
    bot.add_view(MyView())

@bot.command(name='sendrolemessage')
@commands.has_permissions(administrator=True)
async def send_role_message(ctx):
    await ctx.send(config['message'], view=MyView())

# On lance le bot en utilisant la variable d'environnement. 
# Si vous le lancez en local, remplacez-le par bot.run('VOTRE_TOKEN_ICI')
keep_alive()
bot.run(bot_token)