from django.shortcuts import render
from .models import Question

def index(request):
    questions = Question.objects.prefetch_related('choice_set').all()
    return render(request, "polls/index.html", {"questions": questions})
