# TODO Gemini request 
from google import genai
from google.genai.types import GenerateContentConfig

import logging
logger = logging.getLogger(__name__)

gemini_client = genai.Client()

def classify_feedback(feedback_text):

    logger.debug(f'Gemini is classifying this text {feedback_text}')

    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=feedback_text,
        config=GenerateContentConfig(system_instruction="""
        You are a content moderation AI for student feedback submissions.
        You will read the student's feedback and classify it as either
        "genuine" or "spam". Reply with one word, either "genuine" or "spam".
        """)
        )
    
    response_text = response.text
    logger.debug(f'Gemini responded with {response_text}')
    return response_text

if __name__ == '__main__':
    print(classify_feedback('There should be better wifi'))
    print(classify_feedback('win an ipad!!!'))