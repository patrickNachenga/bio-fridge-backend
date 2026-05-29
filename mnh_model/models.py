from django.contrib.auth import get_user_model
from django.db import models

from mnh_auth.models import BaseModel

User = get_user_model()

class StorageFormat(models.TextChoices):
    DRAWERS = "DRAWERS", "Tray → Rack → SampleBox → SampleSpace → Samples"
    BOXES = "BOXES", "SampleBox → SampleSpace → Samples"
    SAMPLES = "SAMPLES", "Samples Only"

class Fridge(BaseModel):
    STATUS_CHOICES = [
        ('NEW', 'NEW'),
        ('ACTIVE', 'Active'),
        ('DAMAGED', 'Damaged'),
        ('FULL', 'Full'),
    ]
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    model = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100)
    minimum_temperature = models.FloatField()
    maximum_temperature = models.FloatField()
    description = models.TextField(blank=True, null=True)  # Optional explanation
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='NEW')
    is_active = models.BooleanField(default=True)
    block_number = models.IntegerField(default=0)
    sample_number = models.IntegerField(default=0)
    capacity = models.IntegerField(default=0)


    class Meta:
        db_table = 'fridges'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.code})"



class FridgeBlock(BaseModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    fridge = models.ForeignKey(Fridge, on_delete=models.CASCADE, related_name='fridge_blocks')
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'fridge_blocks'

    def __str__(self):
        return f"{self.name} ({self.code})"

class FridgePartition(BaseModel):
    block = models.ForeignKey(FridgeBlock, on_delete=models.CASCADE, related_name="fridge_partitions")
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'fridge_partitions'

    def __str__(self):
        return f"{self.block} / {self.name}"

class SampleType(BaseModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'sample_types'
        unique_together = ('name', 'code')

class SampleNature(BaseModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'sample_nature'
        unique_together = ('name', 'code')

class SampleSource(BaseModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'sample_source'
        unique_together = ('name', 'code')

    def __str__(self):
        return f"{self.name} ({self.code})"

class SampleCondition(BaseModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'sample_condition'
        unique_together = ('name', 'code')
        ordering = ('name',)

    def __str__(self):
        return f"{self.name} ({self.code})"

class Project(BaseModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=20, blank=True, null=True)
    type = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = 'project'

    def __str__(self):
        return f"{self.name} ({self.code})"

class ProjectAssignment(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    partition = models.ForeignKey(FridgePartition, on_delete=models.CASCADE)
    format = models.CharField(
        max_length=50,
        choices=StorageFormat.choices,
        default=StorageFormat.SAMPLES
    )

    class Meta:
        db_table = 'project_assignments'

    def __str__(self):
        return f"{self.project} ({self.get_format_display()})"

# ---------  FORMAT 1 ------------
class StorageDrawer(BaseModel):
    assignment = models.ForeignKey(ProjectAssignment, on_delete=models.CASCADE, related_name="storage_drawers")
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'storage_drawers'

class StorageDrawerRack(BaseModel):
    tray = models.ForeignKey(StorageDrawer, on_delete=models.CASCADE, related_name="storage_drawers_racks")
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'storage_drawers_racks'

class StorageDrawerSampleBox(BaseModel):
    rack = models.ForeignKey(StorageDrawerRack, on_delete=models.CASCADE, related_name="storage_drawers_sample_boxes")
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'storage_drawers_sample_boxes'

class StorageDrawerSampleSpace(BaseModel):
    sample_box = models.ForeignKey(StorageDrawerSampleBox, on_delete=models.CASCADE, related_name="storage_drawers_sample_spaces")
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'storage_drawers_sample_spaces'

class StorageDrawerSample(BaseModel):
    sample_space = models.ForeignKey(StorageDrawerSampleSpace, on_delete=models.CASCADE, related_name="storage_drawers_samples")
    code = models.CharField(max_length=50)

    class Meta:
        db_table = 'storage_drawers_samples'


# ---------  FORMAT 2 ------------
class StorageBox(BaseModel):
    assignment = models.ForeignKey(ProjectAssignment, on_delete=models.CASCADE, related_name="storage_boxes")
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'storage_boxes'

class StorageBoxSampleSpace(BaseModel):
    box = models.ForeignKey(StorageBox, on_delete=models.CASCADE, related_name="storage_box_sample_spaces")
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'storage_box_sample_spaces'

class StorageBoxSample(BaseModel):
    sample_space = models.ForeignKey(StorageBoxSampleSpace, on_delete=models.CASCADE, related_name="storage_box_samples")
    code = models.CharField(max_length=50)

    class Meta:
        db_table = 'storage_box_samples'


# ---------  FORMAT 3 ------------
class StorageSample(BaseModel):
    assignment = models.ForeignKey(ProjectAssignment, on_delete=models.CASCADE, related_name="storage_samples")
    code = models.CharField(max_length=50)

    class Meta:
        db_table = 'storage_samples'



        
