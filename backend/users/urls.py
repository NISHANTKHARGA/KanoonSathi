from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('consult/', views.consult, name='consult'),
    path('lawyers/', views.lawyers, name='lawyers'),
    path('appointments/', views.appointments, name='appointments'),
    path('lawyer-register/', views.lawyer_register, name='lawyer_register'),
    path('api/consult', views.consult_ai, name='consult_ai'),
    path('book/<str:lawyer_id>/', views.book_appointment, name='book_appointment'),
]