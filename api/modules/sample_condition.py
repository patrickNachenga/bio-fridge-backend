from datetime import datetime

from django.db import transaction
from django.db.models import Q
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from api.serializers import SampleConditionSerializer
from mnh_fridge.pagination import CustomPagination
from mnh_fridge.response_codes import CustomResponse, STATUS_CODES
from mnh_model.models import SampleCondition

class SampleConditionView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SampleConditionSerializer


    def get(self, request, uid=None):
        try:
            if uid:
                sample_condition = SampleCondition.objects.filter(uid=uid, is_deleted=False).first()
                if not sample_condition:
                    raise NotFound("Sample Condition not found")
                return CustomResponse.success(data=SampleConditionSerializer(sample_condition).data)

            search_query = request.GET.get('search', '').strip()
            sample_conditions = SampleCondition.objects.filter(is_deleted=False)

            if search_query:
                sample_conditions = sample_conditions.filter(
                    Q(name__icontains=search_query) |
                    Q(code__icontains=search_query)
                )

            if sample_conditions.exists():
                return CustomPagination.paginate(view_class=self, results=sample_conditions, request=request)

            return CustomResponse.errors(message="Sample Condition not found", data=[])
        except Exception as e:
            return CustomResponse.server_error(message=f'Failed to Retrieve Sample Conditions: {str(e)}', )

    def post(self, request):
        try:
            with (transaction.atomic()):
                uid = request.data.get('uid', None)
                if uid:
                    try:
                        instance = SampleCondition.objects.get(uid=uid)
                        serializer = self.serializer_class(instance, data=request.data, partial=True)
                    except SampleCondition.DoesNotExist:
                        return CustomResponse.errors(message="Sample Condition not found")

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
            return CustomResponse.server_error(message=f'Failed to Change Sample Condition: {str(e)}', )

    def delete(self, request, uid):
        try:
            with transaction.atomic():
                """ Soft delete a Sample Condition by UID """
                sample_condition = SampleCondition.objects.filter(uid=uid, is_deleted=False).first()
                if not sample_condition:
                    return CustomResponse.errors(message="Sample Condition Not Found or Deleted",)

                sample_condition.is_deleted = True
                sample_condition.deleted_at = datetime.now()
                sample_condition.deleted_by = request.user
                sample_condition.save()
                return CustomResponse.success(message='Sample Condition deleted successfully')

        except Exception as e:
            print("Failed to Delete Sample Condition", str(e))
            return CustomResponse.server_error(message="Something went wrong While Deleting Sample Condition")
