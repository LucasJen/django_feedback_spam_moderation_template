from django.urls import path 
from . import views, moderation_views

urlpatterns  = [
    path('', views.feedback_form, name='feedback_form'),
    path('send_feedback', views.send_feedback, name='send_feedback'),
    path('thank_you', views.thank_you, name='thank_you'),
    path('moderation_feedbkac', moderation_views.moderate_feedback, name='moderate_feedback')
    # TODO add path to moderation request URL
]