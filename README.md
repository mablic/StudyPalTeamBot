# StudyPalTeamBot Discord Bot

StudyPal is a Discord bot designed to help users track their study sessions, manage their time effectively, and practice coding skills. It integrates with voice channels to automatically track study time and provides various commands for managing study sessions and accessing LeetCode questions.

## Features

- Automatic study session tracking in voice channels
- Manual tagging and editing of study sessions
- LeetCode question generator
- Mock interview starter
- Study session information retrieval
- Integration with StudyPal website for detailed study records

## Commands

- `/tag [subject]`: Tag your current study session with a subject (only works in voice channels)
- `/end_session`: Manually end your current study session
- `/session_info`: View details of your current study session
- `/edit_tag [new_subject]`: Edit the tag of your current study session
- `/interview`: Start a mock interview (only works in the mock-interview text channel)
- `/leetcode [difficulty]`: Generate a random LeetCode question (easy/medium/hard, only works in the mock-interview text channel)
- `/website`: Get the link to view your study records
- `/instruction`: Get the link to the bot setup instructions
- `/help`: Display a list of available commands and their descriptions

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up a Discord bot account and get your bot token
4. Set up a Firebase project and download the service account key
5. Create a `.env` file in the project root and add your Discord bot token:
   ```
   DISCORD_BOT_TOKEN=your_bot_token_here
   ```
6. Place your Firebase service account key JSON file in the project root
7. Update the `firebase.py` file with the correct path to your service account key file
8. Run the bot:
   ```
   python bot.py
   ```

## Usage

1. Invite the bot to your Discord server
2. Create a text channel named "mock-interview" for interview and LeetCode commands
3. Create voice channels with "Study Room" in their names for automatic study tracking
4. Use the commands listed above to interact with the bot

## Website Integration

- View your study records: [https://studypalteam.com/](https://studypalteam.com/)
- Access detailed bot setup instructions: [https://studypalteam.com/discordBot](https://studypalteam.com/discordBot)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions, please open an issue on this repository or contact our support team through the StudyPal website.