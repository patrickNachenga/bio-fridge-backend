from datetime import datetime

from django.db import transaction
from django.db.models import Q
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from api.serializers import ProjectSerializer
from mnh_fridge.pagination import CustomPagination
from mnh_fridge.response_codes import CustomResponse, STATUS_CODES
from mnh_model.models import Project

class ProjectView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer


    def get(self, request, uid=None):
        try:
            if uid:
                project = Project.objects.filter(uid=uid, is_deleted=False).first()
                if not project:
                    raise NotFound("Project not found")
                return CustomResponse.success(data=ProjectSerializer(project).data)

            search_query = request.GET.get('search', '').strip()
            projects = Project.objects.filter(is_deleted=False)

            if search_query:
                projects = projects.filter(
                    Q(name__icontains=search_query) |
                    Q(code__icontains=search_query) |
                    Q(phone__icontains=search_query) |
                    Q(email__icontains=search_query) |
                    Q(country__icontains=search_query)
                )

            if projects.exists():
                return CustomPagination.paginate(view_class=self, results=projects, request=request)

            return CustomResponse.errors(message="Project not found", data=[])
        except Exception as e:
            return CustomResponse.server_error(message=f'Failed to Retrieve Projects: {str(e)}', )

    def post(self, request):
        try:
            with (transaction.atomic()):
                uid = request.data.get('uid', None)
                if uid:
                    try:
                        instance = Project.objects.get(uid=uid)
                        serializer = self.serializer_class(instance, data=request.data, partial=True)
                    except Project.DoesNotExist:
                        return CustomResponse.errors(message="Project not found")

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
            return CustomResponse.server_error(message=f'Failed to Change Project: {str(e)}', )

    def delete(self, request, uid):
        try:
            with transaction.atomic():
                """ Soft delete a Project by UID """
                project = Project.objects.filter(uid=uid, is_deleted=False).first()
                if not project:
                    return CustomResponse.errors(message="Project Not Found or Deleted",)

                project.is_deleted = True
                project.deleted_at = datetime.now()
                project.deleted_by = request.user
                project.save()
                return CustomResponse.success(message='Project deleted successfully')

        except Exception as e:
            print("Failed to Delete Project", str(e))
            return CustomResponse.server_error(message="Something went wrong While Deleting Project")
