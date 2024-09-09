from discord import app_commands, Interaction

class HelpCommands(app_commands.Group):
    def __init__(self, bot):
        super().__init__(name="help", description="Help commands for the Study Bot")
        self.bot = bot

    @app_commands.command(name="bot", description="Get help information about the Study Bot")
    async def help_command(self, interaction: Interaction):
        help_text = """
**Available Commands:**

`/tag [subject]`
• Tag your current study session with a subject.
• Only works when you're in a voice channel.

`/end_session`
• Manually end your current study session.

`/session_info`
• View details of your current study session.

`/edit_tag [new_subject]`
• Edit the tag of your current study session.

`/interview`
• Start a mock interview.
• Only works in the #mock-interview channel.

`/leetcode [type]`
• Generate a random LeetCode question.
• Options: easy, medium, hard.
• Only works in the #mock-interview channel.

`/website`
• Get the link to view your study records.

`/instruction`
• Get the link to the bot setup instructions.

`/help`
• Show this help message.

**Note:** The bot tracks your time in voice channels containing 'Study Room'.

**Additional Information:**
• View your study records: https://studypalteam.com/
• Setup instructions: https://studypalteam.com/discordbot
"""
        await interaction.response.send_message(help_text)

    @app_commands.command(name="website", description="Get the link to view your study records")
    async def website_command(self, interaction: Interaction):
        await interaction.response.send_message("You can view your study records at: https://studypalteam.com/")

    @app_commands.command(name="instruction", description="Get the link to the bot setup instructions")
    async def instruction_command(self, interaction: Interaction):
        await interaction.response.send_message("For detailed setup instructions, visit: https://studypalteam.com/discordBot")

def setup(bot):
    bot.tree.add_command(HelpCommands(bot))