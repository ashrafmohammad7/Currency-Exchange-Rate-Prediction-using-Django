from django.urls import path
from . import views

urlpatterns = [
    path('',                views.index,          name='index'),
    path('api/currencies/', views.get_currencies, name='currencies'),
    path('api/historical/', views.get_historical, name='historical'),
    path('api/predict/',    views.predict,        name='predict'),
    path('api/compare/',    views.compare_models, name='compare'),
    path('api/train/',      views.retrain,        name='retrain'),
]

