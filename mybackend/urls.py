from django.urls import path
from api.views import FeedbackView

from api.views import SignUpView
from api.views import LoginView
from api.views import AlertsView,  FeedbackView

urlpatterns = [
    
    path('api/register/', SignUpView.as_view(), name='register'),
    path('api/token/', LoginView.as_view(), name='login'),
    path('api/alerts/', AlertsView.as_view(), name='alert-list'),
   
    path('api/feedback/', FeedbackView.as_view(), name='submit-feedback'),
 
   
]