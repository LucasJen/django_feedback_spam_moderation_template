# TODO create the moderation request function with  code to create start a Cloud Task request 
# TODO create the view that will handle the moderation request 

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseForbidden

from .models import Feedback
from .llm_classifier import classify_feedback

from google.cloud import tasks_v2

import json
import logging

logger = logging.getLogger(__name__)

task_client = tasks_v2.CloudTasksClient()
project = settings.GCP_PROJECT
location = settings.GCP_REGION

def create_moderation_task(feedback_id):
    logger.debug(f'Creating moderation request for feedback {feedback_id}')

    #  GCP can refere ot the queue as the 'parent' of the task
    queue = task_client.queue_path(project, location, 'feedback-moderation-queue')

    # Tasks need 
    # 1. The URL the queue worker will call
    # 2. Payload - data that will be used to complete the task
    # 3. What kind of http method? 
    # 4. Authenticiation - is the task allowed to make this call?

    moderation_url = settings.BASE_URL + reverse('moderate_feedback')
    payload = json.dumps( {'feedback_id': feedback_id} ).encode()

    task = {
        'http_request': {
            'http_method': tasks_v2.HttpMethod.POST,
            'url': moderation_url,
            'headers': {
                'Content-Type': 'application/json',
                'X-Moderation-Task-Secret': settings.MODERATION_TASK_SECRET
            },
            'body': payload
        }
    }

    logger.debug(f'Moderation task: {task}')

    task_client.create_task(request={'parent': queue, 'task': task})

@csrf_exempt
def moderate_feedback(request):
    
    logger.debug('Moderation request recieved')

    # check if the request method is POST
    try: 

        if request.method != 'POST':
            return HttpResponseNotAllowed(['POST'])

        secret = request.headers.get('X-Moderation-Task-Secret')
    
        # check moderation task secret, make sure it matches

        if secret != settings.MODERATION_TASK_SECRET:
            return HttpResponseForbidden()

        # read the feedback id from the request - it will be the payload sent when the task was created

        data = json.loads(request.body) # expects this for {'feedback_id':feedback_id}
        feedback_id = data.get('feedback_id')
    
        # get feedback from database

        feedback = Feedback.objects.get(pk=feedback_id)

        # Make a request to classify the test of the feedback

        classification = classify_feedback(feedback.text)
        
        if classification == 'genuine':
            feedback.status = Feedback.APPROVED
        else:
            feedback.status = Feedback.BLOCKED
    
        # update the database
        feedback.save()
        logger.debug(f'Save feedback object: {feedback}')

        return JsonResponse({'success': True, 'status': classification})

    except Exception as e:
        logger.exception('Error classifying feedback', e)
        return JsonResponse({'success': False, 'error': str(e)}, status=500) #500 = server errors