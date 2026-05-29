from datetime import datetime

from django.db import transaction
from django.db.models import Q, Count
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from api.serializers import FridgeBlockSerializer
from mnh_fridge.pagination import CustomPagination
from mnh_fridge.response_codes import CustomResponse, STATUS_CODES
from mnh_model.models import FridgeBlock, Fridge


class FridgeBlockView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FridgeBlockSerializer

    def get(self, request, fridge_uid=None, block_uid=None):
        try:
            if not fridge_uid:
                return CustomResponse.errors(message="Fridge UID is required")

            # Verify fridge exists
            fridge = Fridge.objects.filter(uid=fridge_uid, is_deleted=False).first()
            if not fridge:
                raise NotFound("Fridge not found")

            if block_uid:
                # Get specific block
                block = FridgeBlock.objects.filter(uid=block_uid, fridge=fridge, is_deleted=False).first()
                if not block:
                    raise NotFound("Block not found")
                return CustomResponse.success(data=FridgeBlockSerializer(block).data)

            # Get all blocks for fridge
            search_query = request.GET.get('search', '').strip()
            blocks = FridgeBlock.objects.filter(fridge=fridge, is_deleted=False)

            if search_query:
                blocks = blocks.filter(
                    Q(name__icontains=search_query) |
                    Q(code__icontains=search_query)
                )

            if blocks.exists():
                return CustomPagination.paginate(view_class=self, results=blocks, request=request)

            return CustomResponse.success(data=[], message="No blocks found")

        except Exception as e:
            return CustomResponse.server_error(message=f'Failed to Retrieve Blocks: {str(e)}')

    def post(self, request, fridge_uid=None):
        try:
            if not fridge_uid:
                return CustomResponse.errors(message="Fridge UID is required")

            with transaction.atomic():
                # Verify fridge exists
                fridge = Fridge.objects.filter(uid=fridge_uid, is_deleted=False).first()
                if not fridge:
                    return CustomResponse.errors(message="Fridge not found")

                block_uid = request.data.get('uid', None)
                if block_uid:
                    try:
                        instance = FridgeBlock.objects.get(uid=block_uid, fridge=fridge)
                        # Create mutable copy
                        data = request.data.copy()
                        data['fridge_uid'] = fridge_uid
                        serializer = self.serializer_class(instance, data=data, partial=True)
                    except FridgeBlock.DoesNotExist:
                        return CustomResponse.errors(message="Block not found")
                else:
                    # Add fridge to data
                    data = request.data.copy()
                    data['fridge_uid'] = fridge_uid
                    serializer = self.serializer_class(data=data)

                if serializer.is_valid():
                    serializer.save(created_by=request.user, updated_by=request.user)
                    return CustomResponse.success(data=serializer.data)

                return CustomResponse.errors(
                    message="Validation Failed",
                    data=serializer.errors,
                    code=STATUS_CODES["VALIDATION_ERROR"],
                )

        except Exception as e:
            return CustomResponse.server_error(message=f'Failed to Save Block: {str(e)}')

    def delete(self, request, fridge_uid, block_uid):
        try:
            with transaction.atomic():
                # Verify fridge exists
                fridge = Fridge.objects.filter(uid=fridge_uid, is_deleted=False).first()
                if not fridge:
                    return CustomResponse.errors(message="Fridge not found")

                block = FridgeBlock.objects.filter(uid=block_uid, fridge=fridge, is_deleted=False).first()
                if not block:
                    return CustomResponse.errors(message="Block not found")

                block.is_deleted = True
                block.deleted_at = datetime.now()
                block.deleted_by = request.user
                block.save()
                return CustomResponse.success(message='Block deleted successfully')

        except Exception as e:
            return CustomResponse.server_error(message=f'Failed to Delete Block: {str(e)}')
