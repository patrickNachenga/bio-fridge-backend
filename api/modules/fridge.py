from datetime import datetime

from django.db import transaction
from django.db.models import Q
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from api.serializers import  FridgeSerializer
from mnh_fridge.pagination import CustomPagination
from mnh_fridge.response_codes import CustomResponse, STATUS_CODES
from mnh_model.models import Fridge

class FridgeView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FridgeSerializer


    def get(self, request, uid=None):
        try:
            if uid:
                fridge = Fridge.objects.filter(uid=uid, is_deleted=False).first()
                if not fridge:
                    raise NotFound("Fridge not found")
                return CustomResponse.success(data=FridgeSerializer(fridge).data)

            search_query = request.GET.get('search', '').strip()
            fridges = Fridge.objects.filter(is_deleted=False)

            if search_query:
                fridges = fridges.filter(
                    Q(name__icontains=search_query) |
                    Q(model__icontains=search_query) |
                    Q(serial_number__icontains=search_query) |
                    Q(code__icontains=search_query)
                )

            if fridges.exists():
                return CustomPagination.paginate(view_class=self, results=fridges, request=request)

            return CustomResponse.errors(message="Fridge not found", data=[])
        except Exception as e:
            return CustomResponse.server_error(message=f'Failed to Retrieve Fridges: {str(e)}', )

    def post(self, request):
        try:
            with (transaction.atomic()):
                uid = request.data.get('uid', None)
                if uid:
                    try:
                        instance = Fridge.objects.get(uid=uid)
                        serializer = self.serializer_class(instance, data=request.data, partial=True)
                    except Fridge.DoesNotExist:
                        return CustomResponse.errors(message="Fridge not found")

                # Handle Create a case (when no uid)
                else:
                    serializer = self.serializer_class(data=request.data)

                # Validate and save
                if serializer.is_valid():
                    serializer.save(created_by=request.user, updated_by=request.user)
                    return CustomResponse.success(data=serializer.data)

                # Validation failed
                return CustomResponse.errors(
                    message="Validation Failed, Please Try Again",
                    data=serializer.errors,
                    code=STATUS_CODES["VALIDATION_ERROR"],
                )

        except Exception as e:
            # Catch unexpected errors that occur in the entire process
            return CustomResponse.server_error(message=f'Failed to Change Fridge: {str(e)}', )

    def delete(self, request, uid):
        try:
            with transaction.atomic():
                """ Soft delete a Fridge by UID """
                fridge = Fridge.objects.filter(uid=uid, is_deleted=False).first()
                if not fridge:
                    return CustomResponse.errors(message="Fridge Not Found or Deleted",)

                fridge.is_deleted = True
                fridge.deleted_at = datetime.now()
                fridge.deleted_by = request.user
                fridge.save()
                return CustomResponse.success(message='Fridge deleted successfully')

        except Exception as e:
            print("Failed to Delete Fridge", str(e))
            return CustomResponse.server_error(message="Something went wrong While Deleting Fridge")
