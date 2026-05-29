from datetime import datetime

from django.db import transaction
from django.db.models import Q
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from api.serializers import SampleTypeSerializer
from mnh_fridge.pagination import CustomPagination
from mnh_fridge.response_codes import CustomResponse, STATUS_CODES
from mnh_model.models import SampleType

class SampleTypeView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SampleTypeSerializer


    def get(self, request, uid=None):
        try:
            if uid:
                sample_type = SampleType.objects.filter(uid=uid, is_deleted=False).first()
                if not sample_type:
                    raise NotFound("Sample Type not found")
                return CustomResponse.success(data=SampleTypeSerializer(sample_type).data)

            search_query = request.GET.get('search', '').strip()
            sample_types = SampleType.objects.filter(is_deleted=False)

            if search_query:
                sample_types = sample_types.filter(
                    Q(name__icontains=search_query) |
                    Q(code__icontains=search_query)
                )

            if sample_types.exists():
                return CustomPagination.paginate(view_class=self, results=sample_types, request=request)

            return CustomResponse.errors(message="Sample Type not found", data=[])
        except Exception as e:
            return CustomResponse.server_error(message=f'Failed to Retrieve Sample Types: {str(e)}', )

    def post(self, request):
        try:
            with (transaction.atomic()):
                uid = request.data.get('uid', None)
                if uid:
                    try:
                        instance = SampleType.objects.get(uid=uid)
                        serializer = self.serializer_class(instance, data=request.data, partial=True)
                    except SampleType.DoesNotExist:
                        return CustomResponse.errors(message="Sample Type not found")

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
            return CustomResponse.server_error(message=f'Failed to Change Sample Type: {str(e)}', )

    def delete(self, request, uid):
        try:
            with transaction.atomic():
                """ Soft delete a Sample Type by UID """
                sample_type = SampleType.objects.filter(uid=uid, is_deleted=False).first()
                if not sample_type:
                    return CustomResponse.errors(message="Sample Type Not Found or Deleted",)

                sample_type.is_deleted = True
                sample_type.deleted_at = datetime.now()
                sample_type.deleted_by = request.user
                sample_type.save()
                return CustomResponse.success(message='Sample Type deleted successfully')

        except Exception as e:
            print("Failed to Delete Sample Type", str(e))
            return CustomResponse.server_error(message="Something went wrong While Deleting Sample Type")
