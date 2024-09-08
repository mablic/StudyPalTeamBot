import logging
import datetime
from discord import app_commands, Interaction, DMChannel
from discord.ext import commands

def cooldown(rate, per_second=0, per_minute=0, per_hour=0, type=commands.BucketType.default):
    return commands.cooldown(rate, per_second or per_minute * 60 or per_hour * 3600, type)

async def tag_command(interaction: Interaction, subject: str, client):
    try:
        user_discord_id = str(interaction.user.id)
        if user_discord_id in client.study_sessions:
            if client.study_sessions[user_discord_id].get('tag'):
                # Send data to the database for the previous tag
                start_time = client.study_sessions[user_discord_id]['start_time']
                end_time = datetime.datetime.now(datetime.timezone.utc)
                duration = (end_time - start_time).total_seconds() / 60  # Convert to minutes
                study_tag = client.study_sessions[user_discord_id]['tag']
                firebase = await client.get_firebase()
                await firebase.send_study_to_database(
                    user_discord_id, 
                    interaction.user.name, 
                    start_time, 
                    client.study_sessions[user_discord_id]['channel_id'],
                    client.study_sessions[user_discord_id]['channel_name'],
                    duration,
                    client.study_sessions[user_discord_id]['server_id'],
                    client.study_sessions[user_discord_id]['server_name'],
                    study_tag
                )
                response_message = f"Previous study session tagged as '{study_tag}' has been recorded. Now studying: {subject}"
                # Update start time and tag for the new session
                client.study_sessions[user_discord_id]['start_time'] = end_time
                client.study_sessions[user_discord_id]['tag'] = subject
            else:
                client.study_sessions[user_discord_id]['tag'] = subject
                response_message = f"Tagged your study subject as: {subject}"
        else:
            response_message = "You're not in a study session. Join a 'Study Room' voice channel to start."
        
        if not isinstance(interaction.channel, DMChannel):
            response_message = "This message is only visible to you.\n\n" + response_message
        await interaction.response.send_message(response_message, ephemeral=True)
    except Exception as e:
        logging.error(f"Error in tag_command: {str(e)}")
        await interaction.response.send_message("An error occurred while processing your request. Please try again later.", ephemeral=True)

async def end_session_command(interaction: Interaction, client):
    try:
        user_discord_id = str(interaction.user.id)
        if user_discord_id in client.study_sessions:
            await end_study_session(interaction.user, client)
            response_message = "Your study session has been ended manually."
        else:
            response_message = "You don't have an active study session."
        if not isinstance(interaction.channel, DMChannel):
            response_message = "This message is only visible to you.\n\n" + response_message
        
        await interaction.response.send_message(response_message, ephemeral=True)
    except Exception as e:
        logging.error(f"Error in end_session_command: {str(e)}")
        await interaction.response.send_message("An error occurred while ending your session. Please try again later.", ephemeral=True)

async def session_info_command(interaction: Interaction, client):
    try:
        user_discord_id = str(interaction.user.id)
        if user_discord_id in client.study_sessions:
            session = client.study_sessions[user_discord_id]
            start_time = session['start_time']
            current_time = datetime.datetime.now(datetime.timezone.utc)
            duration = (current_time - start_time).total_seconds() / 60  # Minutes
            subject = session.get('tag', 'Not tagged')
            response_message = f"Current session info:\nSubject: {subject}\nDuration: {duration:.2f} minutes\nStarted at: {start_time.strftime('%Y-%m-%d %H:%M:%S')} UTC"
        else:
            response_message = "You don't have an active study session."
        
        if not isinstance(interaction.channel, DMChannel):
            response_message = "This message is only visible to you.\n\n" + response_message
        
        await interaction.response.send_message(response_message, ephemeral=True)
    except Exception as e:
        logging.error(f"Error in session_info_command: {str(e)}")
        await interaction.response.send_message("An error occurred while retrieving your session info. Please try again later.", ephemeral=True)

async def new_tag_command(interaction: Interaction, new_subject: str, client):
    try:
        user_discord_id = str(interaction.user.id)
        if user_discord_id in client.study_sessions:
            # Send existing data to the database
            start_time = client.study_sessions[user_discord_id]['start_time']
            end_time = datetime.datetime.now(datetime.timezone.utc)
            duration = (end_time - start_time).total_seconds() / 60  # Convert to minutes
            old_tag = client.study_sessions[user_discord_id].get('tag', 'Not tagged')
            
            firebase = await client.get_firebase()
            await firebase.send_study_to_database(
                user_discord_id, 
                interaction.user.name, 
                start_time, 
                client.study_sessions[user_discord_id]['channel_id'],
                client.study_sessions[user_discord_id]['channel_name'],
                duration,
                client.study_sessions[user_discord_id]['server_id'],
                client.study_sessions[user_discord_id]['server_name'],
                old_tag
            )
            
            # Reset start time and update tag for the new session
            client.study_sessions[user_discord_id]['start_time'] = end_time
            client.study_sessions[user_discord_id]['tag'] = new_subject
            
            response_message = f"Previous study session tagged as '{old_tag}' has been recorded (duration: {duration:.2f} minutes). New study session started with tag: {new_subject}"
        else:
            # Start a new study session if one doesn't exist
            client.study_sessions[user_discord_id] = {
                'start_time': datetime.datetime.now(datetime.timezone.utc),
                'channel_id': str(interaction.channel.id),
                'channel_name': interaction.channel.name,
                'server_id': str(interaction.guild.id),
                'server_name': interaction.guild.name,
                'tag': new_subject
            }
            response_message = f"New study session started with tag: {new_subject}"
        
        if not isinstance(interaction.channel, DMChannel):
            response_message = "This message is only visible to you.\n\n" + response_message
        
        await interaction.response.send_message(response_message, ephemeral=True)
    except Exception as e:
        logging.error(f"Error in new_tag_command: {str(e)}")
        await interaction.response.send_message("An error occurred while processing your request. Please try again later.", ephemeral=True)

async def edit_tag_command(interaction: Interaction, new_subject: str, client):
    try:
        user_discord_id = str(interaction.user.id)
        if user_discord_id in client.study_sessions:
            old_tag = client.study_sessions[user_discord_id].get('tag', 'Not tagged')
            client.study_sessions[user_discord_id]['tag'] = new_subject
            response_message = f"Your study tag has been updated from '{old_tag}' to '{new_subject}'."
        else:
            response_message = "You don't have an active study session."
        
        if not isinstance(interaction.channel, DMChannel):
            response_message = "This message is only visible to you.\n\n" + response_message
        
        await interaction.response.send_message(response_message, ephemeral=True)
    except Exception as e:
        logging.error(f"Error in edit_tag_command: {str(e)}")
        await interaction.response.send_message("An error occurred while editing your tag. Please try again later.", ephemeral=True)

async def end_study_session(member, client):
    user_discord_id = str(member.id)
    if user_discord_id in client.study_sessions:
        start_time = client.study_sessions[user_discord_id]['start_time']
        end_time = datetime.datetime.now(datetime.timezone.utc)
        duration = (end_time - start_time).total_seconds() / 60  # Convert to minutes
        channel_id = client.study_sessions[user_discord_id]['channel_id']
        channel_name = client.study_sessions[user_discord_id]['channel_name']
        server_id = client.study_sessions[user_discord_id]['server_id']
        server_name = client.study_sessions[user_discord_id]['server_name']
        study_tag = client.study_sessions[user_discord_id].get('tag') or 'study'
        try:
            # Send study data to Firebase
            firebase = await client.get_firebase()
            await firebase.send_study_to_database(
                user_discord_id, 
                member.name, 
                start_time, 
                channel_id,
                channel_name,
                duration,
                server_id,
                server_name,
                study_tag
            )
            del client.study_sessions[user_discord_id]
            await member.send(f"Finished Timing! You studied {study_tag} for {duration:.2f} minutes in {channel_name} on {server_name}. Visit our website to view your data.")
        except Exception as e:
            logging.error(f"Error ending study session for user {user_discord_id}: {str(e)}")
            await member.send("An error occurred while ending your study session. Please try again or contact support if the issue persists.")

def setup(client):
    @client.tree.command(name="tag", description="Tag your study subject")
    @app_commands.describe(subject="The subject you're studying")
    @cooldown(rate=1, per_minute=1, type=commands.BucketType.user)
    async def tag_wrapper(interaction: Interaction, subject: str):
        await tag_command(interaction, subject, client)

    @client.tree.command(name="end_session", description="Manually end your current study session")
    async def end_session_wrapper(interaction: Interaction):
        await end_session_command(interaction, client)

    @client.tree.command(name="session_info", description="View details of your current study session")
    async def session_info_wrapper(interaction: Interaction):
        await session_info_command(interaction, client)

    @client.tree.command(name="new_tag", description="Start a new study session with a new tag")
    @app_commands.describe(new_subject="The new subject you're starting to study")
    @cooldown(rate=1, per_minute=1, type=commands.BucketType.user)
    async def new_tag_wrapper(interaction: Interaction, new_subject: str):
        await new_tag_command(interaction, new_subject, client)

    @client.tree.command(name="edit_tag", description="Edit the tag of your current study session")
    @app_commands.describe(new_subject="The new subject you're studying")
    async def edit_tag_wrapper(interaction: Interaction, new_subject: str):
        await edit_tag_command(interaction, new_subject, client)