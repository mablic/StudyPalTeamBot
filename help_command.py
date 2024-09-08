from discord import app_commands, Interaction

def help_command(interaction: Interaction):
    help_text = """
**Available Commands:**

1. `/tag [subject]`
   Tag your current study session with a subject.
   (Only works when you're in a voice channel)

2. `/end_session`
   Manually end your current study session.

3. `/session_info`
   View details of your current study session.

4. `/edit_tag [new_subject]`
   Edit the tag of your current study session.

5. `/interview [type]`
   Start a mock interview.

6. `/help`
   Show this help message.

The bot tracks your time in voice channels containing 'Study Room'.

**Additional Information:**
• View your study records at: https://studypalteam.com/
• For detailed setup instructions, visit: https://studypalteam.com/discordBot
"""
    return interaction.response.send_message(help_text)

def setup(bot):
    @bot.tree.command(name="help", description="Get help information about the Study Bot")
    async def help_wrapper(interaction: Interaction):
        await help_command(interaction)