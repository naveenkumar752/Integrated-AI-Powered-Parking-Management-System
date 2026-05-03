from django.urls import path
from . import views

urlpatterns = [
    path('', views.base, name='base'),  # Home page
    path('index/', views.index, name='index'),  # Home page
    path('capture_and_process/', views.capture_and_process, name='capture_and_process'),
    path('parking_slots/', views.parking_slots, name='parking_slots'),
    path('result/', views.result, name='result'),
    path('get_parking_slots/', views.get_parking_slots, name='get_parking_slots'),
    path('start_parking_transaction/<str:slot_number>', views.start_parking_transaction, name='start_parking_transaction'),
    path('end_parking_transaction/<str:lpnum>/', views.end_parking_transaction, name='end_parking_transaction'),
    path('payment/',views.payment,name='payment'),
    path('transaction_receipt/', views.transaction_receipt, name='transaction_receipt'),
]