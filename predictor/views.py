from django.http import HttpResponse, JsonResponse

def index(request):
    return HttpResponse("Currency Exchange Prediction App Running Successfully!")

def get_currencies(request):
    return JsonResponse({"message": "currencies api working"})

def get_historical(request):
    return JsonResponse({"message": "historical api working"})

def predict(request):
    return JsonResponse({"message": "prediction api working"})

def compare_models(request):
    return JsonResponse({"message": "compare api working"})

def retrain(request):
    return JsonResponse({"message": "retrain api working"})