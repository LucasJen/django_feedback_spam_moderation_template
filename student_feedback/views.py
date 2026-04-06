from django.shortcuts import render, redirect
from .forms import FeedbackForm
from django.http import HttpResponseNotAllowed
from .moderation_views import create_moderation_task


def feedback_form(request):
    feedback_form = FeedbackForm()
    return render(request, 'student_feedback/feedback_form.html', {'feedback_form': feedback_form})


def send_feedback(request):
    if request.method != 'POST':       # Ensure POST request 
        return HttpResponseNotAllowed(['POST'])
    else:
        form = FeedbackForm(request.POST)
        feedback = form.save()  # make new feedback object in memory, not in DB
        if form.is_valid():
            feedback.save()   # Save to the database
            # calls the moderation task function from moderation_views
            create_moderation_task(feedback.pk)

            return redirect('thank_you')
        else:
            return redirect('send_feedback')  # back to home page 


def thank_you(request):
    return render(request, 'student_feedback/thank_you.html')


