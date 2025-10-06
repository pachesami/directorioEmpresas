from django.shortcuts import render
    


def signip (request):
    return render(request, 'signip.html')

def signup (request):
    return render(request, 'signup.html')

def home (request):
    return render(request, 'home.html')




