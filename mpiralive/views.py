from datetime import datetime

from django.db import transaction
from django.db.models import Q
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView

from api.serializers import  FridgeSerializer
from mnh_fridge.pagination import CustomPagination
from mnh_fridge.response_codes import CustomResponse, STATUS_CODES
from mnh_model.models import Fridge
from mpiralive.services import FawaNewsScraper


class MpiraLiveView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        data = FawaNewsScraper.get_matches()
        if data:
            return CustomResponse.success(data=data, message="Football matches fetched successfully")
        return CustomResponse.errors(message="No match data found")
