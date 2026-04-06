from django.contrib import admin
from .models import Feedback

# TODO create a filter to only display approved feedback 
class FeedbackAdmin(admin.ModelAdmin):
    list_filter = ['status']


admin.site.register(Feedback, FeedbackAdmin)
