from datetime import datetime

from django.db import transaction
from django.db.models import Q
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from api.serializers import FridgePartitionSerializer
from mnh_fridge.pagination import CustomPagination
from mnh_fridge.response_codes import CustomResponse, STATUS_CODES
from mnh_model.models import FridgePartition, FridgeBlock, Fridge


class FridgePartitionView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FridgePartitionSerializer

    def get(self, request, fridge_uid=None, block_uid=None, partition_uid=None):
        try:
            if not fridge_uid or not block_uid:
                return CustomResponse.errors(message="Fridge UID and Block UID are required")

            # Verify fridge and block exist
            fridge = Fridge.objects.filter(uid=fridge_uid, is_deleted=False).first()
            if not fridge:
                raise NotFound("Fridge not found")

            block = FridgeBlock.objects.filter(uid=block_uid, fridge=fridge, is_deleted=False).first()
            if not block:
                raise NotFound("Block not found")

            if partition_uid:
                # Get specific partition
                partition = FridgePartition.objects.filter(uid=partition_uid, block=block, is_deleted=False).first()
                if not partition:
                    raise NotFound("Partition not found")
                return CustomResponse.success(data=FridgePartitionSerializer(partition).data)

            # Get all partitions for block
            search_query = request.GET.get('search', '').strip()
            partitions = FridgePartition.objects.filter(block=block, is_deleted=False)

            if search_query:
                partitions = partitions.filter(Q(name__icontains=search_query))

            if partitions.exists():
                return CustomPagination.paginate(view_class=self, results=partitions, request=request)

            return CustomResponse.success(data=[], message="No partitions found")

        except Exception as e:
            return CustomResponse.server_error(message=f'Failed to Retrieve Partitions: {str(e)}')

    def post(self, request, fridge_uid=None, block_uid=None):
        try:
            if not fridge_uid or not block_uid:
                return CustomResponse.errors(message="Fridge UID and Block UID are required")

            with transaction.atomic():
                # Verify fridge and block exist
                fridge = Fridge.objects.filter(uid=fridge_uid, is_deleted=False).first()
                if not fridge:
                    return CustomResponse.errors(message="Fridge not found")

                block = FridgeBlock.objects.filter(uid=block_uid, fridge=fridge, is_deleted=False).first()
                if not block:
                    return CustomResponse.errors(message="Block not found")

                partition_uid = request.data.get('uid', None)
                if partition_uid:
                    try:
                        instance = FridgePartition.objects.get(uid=partition_uid, block=block)
                        # Create mutable copy
                        data = request.data.copy()
                        data['block_uid'] = block_uid
                        serializer = self.serializer_class(instance, data=data, partial=True)
                    except FridgePartition.DoesNotExist:
                        return CustomResponse.errors(message="Partition not found")
                else:
                    # Add block to data
                    data = request.data.copy()
                    data['block_uid'] = block_uid
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
            return CustomResponse.server_error(message=f'Failed to Save Partition: {str(e)}')

    def delete(self, request, fridge_uid, block_uid, partition_uid):
        try:
            with transaction.atomic():
                # Verify fridge and block exist
                fridge = Fridge.objects.filter(uid=fridge_uid, is_deleted=False).first()
                if not fridge:
                    return CustomResponse.errors(message="Fridge not found")

                block = FridgeBlock.objects.filter(uid=block_uid, fridge=fridge, is_deleted=False).first()
                if not block:
                    return CustomResponse.errors(message="Block not found")

                partition = FridgePartition.objects.filter(uid=partition_uid, block=block, is_deleted=False).first()
                if not partition:
                    return CustomResponse.errors(message="Partition not found")

                partition.is_deleted = True
                partition.deleted_at = datetime.now()
                partition.deleted_by = request.user
                partition.save()
                return CustomResponse.success(message='Partition deleted successfully')

        except Exception as e:
            return CustomResponse.server_error(message=f'Failed to Delete Partition: {str(e)}')
