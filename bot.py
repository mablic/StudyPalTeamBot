import os
import logging
from dotenv import load_dotenv
import discord
from discord import app_commands
from firebase import FIREBASE
import datetime
from discord.ext import commands
import help_command
import tag_commands
from random_bq_list import bq_select

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Load environment variables
load_dotenv()

# Discord bot setup
class MyClient(discord.Client):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.study_sessions = {}
        self.FIREBASE = FIREBASE()

    async def setup_hook(self):
        # Add the HelpCommands group to the command tree
        help_command.setup(self)
        # Set up tag commands
        tag_commands.setup(self) 
        # Sync commands with Discord
        await self.tree.sync()
        logging.info("Commands synced with Discord")

    async def get_firebase(self):
        return self.FIREBASE

    async def log_command(self, interaction: discord.Interaction):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        server_name = interaction.guild.name if interaction.guild else "DM"
        server_id = interaction.guild.id if interaction.guild else "N/A"
        channel_name = interaction.channel.name if isinstance(interaction.channel, discord.TextChannel) else "DM"
        channel_id = interaction.channel.id
        username = interaction.user.name
        user_id = interaction.user.id
        command = interaction.command.name if interaction.command else "Unknown"
        
        # More robust option handling
        options = []
        if "options" in interaction.data:
            for option in interaction.data["options"]:
                if "value" in option:
                    options.append(f"{option['name']}:{option['value']}")
                elif "options" in option:  # For subcommands
                    suboptions = [f"{suboption['name']}:{suboption.get('value', 'N/A')}" for suboption in option["options"]]
                    options.append(f"{option['name']}({','.join(suboptions)})")
                else:
                    options.append(f"{option['name']}:N/A")
        options_str = " ".join(options)

        log_entry = f"{current_time}|{server_name}|{server_id}|{channel_name}|{channel_id}|{username}|{user_id}|/{command} {options_str}\n"

        try:
            with open("log.txt", "a", encoding="utf-8") as log_file:
                log_file.write(log_entry)
        except Exception as e:
            logging.error(f"Failed to write to log file: {str(e)}")

client = MyClient()

@client.tree.command(name="leetcode", description="Get a random LeetCode question")
@app_commands.describe(difficulty="The difficulty of the LeetCode question (Easy, Medium, Hard)")
async def leetcode(interaction: discord.Interaction, difficulty: str = None):
    if interaction.channel.name != "mock-interview":
        await interaction.response.send_message("This command can only be used in the #mock-interview channel.", ephemeral=True)
        return
    await interaction.response.defer()
    firebase = await client.get_firebase()
    question = await firebase.get_leetcode_questions(difficulty)
    await interaction.followup.send(question)

@client.tree.command(name="interview", description="Start a mock behavior question interview")
async def interview_command(interaction: discord.Interaction):
    if interaction.channel.name != "mock-interview":
        await interaction.response.send_message("This command can only be used in the #mock-interview channel.", ephemeral=True)
        return
    # Implement your interview command logic here
    await interaction.response.send_message(f"Starting a mock interview of type: {bq_select()}")

@client.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.application_command:
        await client.log_command(interaction)

@client.event
async def on_voice_state_update(member, before, after):
    user_discord_id = str(member.id)
    
    if after.channel and 'Study Room' in after.channel.name:
        if user_discord_id not in client.study_sessions:
            # Start of study session
            client.study_sessions[user_discord_id] = {
                'start_time': datetime.datetime.now(datetime.timezone.utc),
                'channel_id': str(after.channel.id),
                'channel_name': after.channel.name,
                'server_id': str(after.channel.guild.id),
                'server_name': after.channel.guild.name,
                'tag': None
            }
            await member.send("Start Timing! Use /tag [subject] to add your focus.")
    
    elif before.channel and 'Study Room' in before.channel.name and (not after.channel or 'Study Room' not in after.channel.name):
        # End of study session
        await tag_commands.end_study_session(member, client)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

if __name__ == '__main__':
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    try:
        client.run(TOKEN)
    except Exception as e:
        logging.error(f"Failed to start the bot: {str(e)}")