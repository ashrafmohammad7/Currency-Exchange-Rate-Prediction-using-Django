from django.http import HttpResponse

def home(request):
    return HttpResponse("Currency Exchange Prediction App Working Successfully!")