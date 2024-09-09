import os
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
from decimal import Decimal, ROUND_HALF_UP
import random

# Firebase setup
cred = credentials.Certificate("studypaldev01-firebase-adminsdk-c0m76-d5526fe019.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

class FIREBASE:
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance
    
    def __init__(self):
        self.TOKEN = os.getenv('DISCORD_BOT_TOKEN')
        self.db = firestore.client()  # Initialize db here

    async def send_study_to_database(self, user_discord_id, user_discord_name, start_time, 
            channel_id, channel_name, duration, server_id, server_name, study_tag):
        try:
            # Round duration to 2 decimal places
            rounded_duration = Decimal(duration).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            study_doc_ref = self.db.collection('users_study')
            query = study_doc_ref.where(field_path='userDiscordId', op_string='==', value=user_discord_id)
            study_docs = query.get()
            
            if not study_docs:
                # No document found, create a new one
                user_doc_ref = self.db.collection('users').document(user_discord_id)
                user_snapshot = user_doc_ref.get()
                initial_data = {
                    'userDiscordId': user_discord_id,
                    'userDiscordName': user_discord_name,
                    'studyDetails': [],
                    'discordChannelId': channel_id,
                    'discordChannelName': channel_name,
                    'discordServerId': server_id,
                    'discordServerName': server_name
                }
                
                if user_snapshot.exists:
                    user_data = user_snapshot.to_dict()
                    initial_data.update({
                        'userId': user_data.get('uid', ''),
                        'userName': user_data.get('displayName', ''),
                        'userPhotoURL': user_data.get('userPhotoURL', '')
                    })
                
                new_doc_ref = study_doc_ref.document()
                new_doc_ref.set(initial_data)
                study_data = initial_data
            else:
                # Use the first matching document
                study_doc = study_docs[0]
                study_data = study_doc.to_dict()
                new_doc_ref = study_doc.reference

            study_details = study_data.get('studyDetails', [])
            # Convert start_time to UTC
            start_time_utc = start_time.replace(tzinfo=datetime.timezone.utc)
            duplicate_found = False
            for i, detail in enumerate(study_details):
                detail_date = datetime.datetime.fromisoformat(detail['createdAt'].rstrip('Z')).replace(tzinfo=datetime.timezone.utc)
                if (detail['studyTopic'] == study_tag and
                    detail_date.year == start_time_utc.year and
                    detail_date.month == start_time_utc.month and
                    detail_date.day == start_time_utc.day and
                    detail_date.hour == start_time_utc.hour):
                    study_details[i]['studyNumber'] = float(Decimal(str(study_details[i]['studyNumber'])) + rounded_duration)
                    duplicate_found = True
                    break
            if not duplicate_found:
                new_detail = {
                    'studyTopic': study_tag,
                    'createdAt': start_time_utc.isoformat(),
                    'studyNumber': float(rounded_duration)
                }
                study_details.append(new_detail)

            new_doc_ref.update({'studyDetails': study_details})
        except Exception as error:
            print(f"send_study_to_database error: {error}")
            raise error
    
    async def get_leetcode_questions(self, type=None):
        leetcode_doc_ref = self.db.collection('leetcode_questions').document('0')
        leetcode_snapshot = leetcode_doc_ref.get()  # Remove 'await' as firestore operations are synchronous
        if leetcode_snapshot.exists:
            questions = leetcode_snapshot.to_dict().get('Details', [])
            # Filter questions based on type if specified
            if type:
                type = type.capitalize()  # Ensure correct capitalization
                filtered_questions = [q for q in questions if q['hardType'] == type]
            else:
                filtered_questions = questions

            if not filtered_questions:
                return "No questions found for the specified difficulty."
            # Randomly select a question
            selected_question = random.choice(filtered_questions)
            # Prepare the response
            response = (
                f"Here's a random {selected_question['hardType']} LeetCode question for you:\n"
                f"Question: {selected_question['questionName']} (#{selected_question['questionNo']})\n"
                f"Type: {selected_question['questionType']}\n"
                f"Acceptance Rate: {selected_question['accptRate']}\n"
                f"Link: {selected_question['link']}"
            )
            return response
        else:
            return "No LeetCode questions found in the database."
