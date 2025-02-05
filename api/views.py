from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime
from bson.objectid import ObjectId
from .mongo_utils import get_mongo_db
from .serializers import FeedbackSerializer, SignUpSerializer, LoginSerializer

# ===========================
# Feedback Views
# ===========================
from django.http import JsonResponse
from django.views import View
from bson import ObjectId
from datetime import datetime
from .mongo_utils import get_all_alerts_with_transactions, get_alert_with_transactions, submit_feedback


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import mongo_utils
from .serializers import AlertSerializer, FeedbackSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
  # Assuming you have utility functions for MongoDB

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError


class AlertsView(View):
    def get(self, request):
        """
        Get a list of alerts with associated transactions, paginated.
        """
        try:
            limit = int(request.GET.get('limit', 3))  # Default to 3 alerts per request
            skip = int(request.GET.get('skip', 0))    # Default to starting from the first alert
            alerts = get_all_alerts_with_transactions(limit, skip)
            return JsonResponse({'status': 'success', 'data': alerts}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

class AlertDetailView(View):
    def get(self, request, alert_id):
        """
        Get a specific alert with its associated transactions.
        """
        try:
            alert = get_alert_with_transactions(alert_id)
            if alert:
                return JsonResponse({'status': 'success', 'data': alert}, status=200)
            return JsonResponse({'status': 'error', 'message': 'Alert not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)





class FeedbackView(APIView):
    def post(self, request):
        """Submit feedback for an alert."""
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            feedback_id = mongo_utils.submit_feedback(serializer.validated_data)
            return Response({"message": "Feedback submitted successfully", "id": feedback_id}, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



# ===========================
# Authentication Views
# ===========================

class SignUpView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)


# ===========================
# Alert History Views
# ===========================


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status



