from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from mnh_auth.serializers import UserSerializer
from mnh_model.models import (
    Project, SampleType, Fridge, FridgeBlock,
    StorageDrawer, StorageDrawerSample, SampleSource, SampleCondition, SampleNature, ProjectAssignment, StorageFormat,
    StorageSample,
    StorageDrawerSampleSpace, StorageDrawerSampleBox, StorageDrawerRack, StorageBoxSample, StorageBoxSampleSpace,
    StorageBox, FridgePartition
)


class UidPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def to_internal_value(self, data):
        try:
            return self.queryset.get(uid=data)
        except self.queryset.model.DoesNotExist:
            raise serializers.ValidationError(f"Invalid UID: {data}")

    def to_representation(self, value):
        return value.uid


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'uid', 'name', 'code', 'description', 'created_at', 'updated_at', 'is_active',
            'email', 'phone', 'country', 'type'
        ]
        read_only_fields = ['uid', 'created_at', 'updated_at']
        extra_kwargs = {
            'created_by': {'read_only': True},
            'updated_by': {'read_only': True},
            'deleted_by': {'read_only': True},
        }


class SampleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleType
        fields = [
            'uid', 'name', 'code', 'description', 'created_at', 'updated_at', 'created_by', 'updated_by', 'deleted_by'
        ]
        read_only_fields = ['uid', 'created_at', 'updated_at', 'created_by', 'updated_by', 'deleted_by']


class SampleSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleSource
        fields = [
            'uid', 'name', 'code', 'description', 'created_at', 'updated_at', 'created_by', 'updated_by', 'deleted_by'
        ]
        read_only_fields = ['uid', 'created_at', 'updated_at', 'created_by', 'updated_by', 'deleted_by']


class SampleConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleCondition
        fields = [
            'uid', 'name', 'code', 'description', 'created_at', 'updated_at', 'created_by', 'updated_by', 'deleted_by'
        ]
        read_only_fields = ['uid', 'created_at', 'updated_at', 'created_by', 'updated_by', 'deleted_by']


class SampleNatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleNature
        fields = [
            'uid', 'name', 'code', 'description', 'created_at', 'updated_at', 'created_by', 'updated_by', 'deleted_by'
        ]
        read_only_fields = ['uid', 'created_at', 'updated_at', 'created_by', 'updated_by', 'deleted_by']


class FridgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fridge
        fields = [
            'uid', 'name', 'code', 'description', 'created_at', 'updated_at', 'status', 'is_active',
            'model', 'serial_number', 'minimum_temperature', 'maximum_temperature', 'created_at', 'updated_at',
            'block_number', 'sample_number', 'capacity'
        ]
        read_only_fields = ['uid', 'created_at', 'updated_at', 'status']
        extra_kwargs = {
            'created_by': {'read_only': True},
            'updated_by': {'read_only': True},
            'deleted_by': {'read_only': True},
        }

class FridgePartitionInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)



class FridgePartitionSerializer(serializers.ModelSerializer):
    block_uid = serializers.UUIDField(write_only=True, required=False)
    block = serializers.SerializerMethodField()

    class Meta:
        model = FridgePartition
        fields = ['uid', 'name', 'block_uid', 'block', 'created_at', 'updated_at', 'created_by', 'updated_by', 'deleted_by']
        read_only_fields = ['uid','created_at', 'updated_at', 'created_by', 'updated_by', 'deleted_by', 'block']

    def get_block(self, obj):
        return {'uid': str(obj.block.uid), 'name': obj.block.name, 'code': obj.block.code}

    def validate(self, data):
        block_uid = data.get('block_uid')
        if block_uid:
            try:
                data['block'] = FridgeBlock.objects.get(uid=block_uid, is_deleted=False)
            except FridgeBlock.DoesNotExist:
                raise serializers.ValidationError({"block_uid": f"Block {block_uid} not found or deleted."})
        return data

    def create(self, validated_data):
        validated_data.pop('block_uid', None)
        return super().create(validated_data)



class FridgeBlockSerializer(serializers.ModelSerializer):
    fridge_uid = serializers.UUIDField(write_only=True, required=False)
    number_partitions = serializers.IntegerField(write_only=True, default=1, min_value=1, required=False)
    fridge = serializers.SerializerMethodField()

    partitions_details = FridgePartitionSerializer(source='fridge_partitions', read_only=True, many=True)

    class Meta:
        model = FridgeBlock
        fields = [
            'uid','name','code', 'description','is_active','fridge_uid', 'fridge', 'number_partitions', 'partitions_details',
            'created_at', 'updated_at', 'created_by', 'updated_by', 'deleted_by'
        ]
        read_only_fields = ['uid','created_at', 'updated_at', 'created_by', 'updated_by', 'deleted_by', 'fridge']

    def get_fridge(self, obj):
        return {'uid': str(obj.fridge.uid), 'name': obj.fridge.name}

    def validate(self, data):
        fridge_uid = data.get('fridge_uid')
        if fridge_uid:
            data['code'] = str(data.get('code', '')).replace(' ', '_').upper()
            try:
                data['fridge'] = Fridge.objects.get(uid=fridge_uid, is_deleted=False)
            except Fridge.DoesNotExist:
                raise serializers.ValidationError({"fridge_uid": f"Fridge {fridge_uid} not found or deleted."})
        return data

    def create(self, validated_data):
        partitions = int(validated_data.pop('number_partitions', 1))
        validated_data.pop('fridge_uid', None)

        # Create the block
        block = FridgeBlock.objects.create(**validated_data)

        # Create the partitions
        for part in range(partitions):
            FridgePartition.objects.create(
                block=block,
                name=f'{block.code}-0{part+1}',
                created_by=validated_data.get('created_by'),
                updated_by=validated_data.get('updated_by'),
            )
        return block


class ProjectAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectAssignment
        fields = ["id", "project", "partition", "format"]

    def validate_format(self, value):
        if value not in StorageFormat.values:
            raise serializers.ValidationError("Invalid storage format selected.")
        return value


# class SampleSerializer(serializers.ModelSerializer):
#     box_uid = UidPrimaryKeyRelatedField(source='box', queryset=Box.objects.all(), write_only=True)
#     box_gap_uid = UidPrimaryKeyRelatedField(source='box_gap', queryset=BoxGap.objects.all(), write_only=True)
#     type_uid = UidPrimaryKeyRelatedField(source='type', queryset=SampleType.objects.all(), write_only=True)
#
#     box = BoxSerializer(read_only=True)
#     box_gap = BoxGapSerializer(read_only=True)
#     type = SampleTypeSerializer(read_only=True)
#
#     class Meta:
#         model = Sample
#         fields = '__all__'

class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageDrawerSample
        fields = ["id", "code"]


class SampleSpaceSerializer(serializers.ModelSerializer):
    samples = SampleSerializer(many=True, read_only=True)

    class Meta:
        model = StorageDrawerSampleSpace
        fields = ["id", "name", "samples"]


class SampleBoxSerializer(serializers.ModelSerializer):
    sample_spaces = SampleSpaceSerializer(many=True, read_only=True)

    class Meta:
        model = StorageDrawerSampleBox
        fields = ["id", "name", "sample_spaces"]


class RackSerializer(serializers.ModelSerializer):
    sample_boxes = SampleBoxSerializer(many=True, read_only=True)

    class Meta:
        model = StorageDrawerRack
        fields = ["id", "name", "sample_boxes"]


class TraySerializer(serializers.ModelSerializer):
    racks = RackSerializer(many=True, read_only=True)

    class Meta:
        model = StorageDrawer
        fields = ["id", "name", "racks"]


class BoxSampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageBoxSample
        fields = ["id", "code"]


class BoxSampleSpaceSerializer(serializers.ModelSerializer):
    samples = BoxSampleSerializer(many=True, read_only=True)

    class Meta:
        model = StorageBoxSampleSpace
        fields = ["id", "name", "samples"]


class BoxOnlySerializer(serializers.ModelSerializer):
    sample_spaces = BoxSampleSpaceSerializer(many=True, read_only=True)

    class Meta:
        model = StorageBox
        fields = ["id", "name", "sample_spaces"]


class DirectSampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageSample
        fields = ["id", "code"]


class ProjectAssignmentDetailSerializer(serializers.ModelSerializer):
    trays = TraySerializer(many=True, read_only=True)
    boxes_only = BoxOnlySerializer(many=True, read_only=True)
    direct_samples = DirectSampleSerializer(many=True, read_only=True)

    class Meta:
        model = ProjectAssignment
        fields = [
            "id",
            "project",
            "partition",
            "format",
            "trays",
            "boxes_only",
            "direct_samples"
        ]
