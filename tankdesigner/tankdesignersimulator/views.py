from django.shortcuts import render

# Create your views here.
def design(request):
    return render(request,'design.html')