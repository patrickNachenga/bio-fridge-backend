from django.urls import path

from api.modules.fridge import FridgeView
from api.modules.fridge_block import FridgeBlockView
from api.modules.fridge_partition import FridgePartitionView
from api.modules.project import ProjectView
from api.modules.sample_condition import SampleConditionView
from api.modules.sample_nature import SampleNatureView
from api.modules.sample_source import SampleSourceView
from api.modules.sample_type import SampleTypeView

urlpatterns = [
    path('projects', ProjectView.as_view(), name='project-view'),
    path('projects/<str:uid>', ProjectView.as_view(), name='project-one'),

    path('sample-types', SampleTypeView.as_view(), name='sample-type-view'),
    path('sample-types/<str:uid>', SampleTypeView.as_view(), name='sample-type-one'),

    path('sample-sources', SampleSourceView.as_view(), name='sample-source-view'),
    path('sample-sources/<str:uid>', SampleSourceView.as_view(), name='sample-source-one'),

    path('sample-conditions', SampleConditionView.as_view(), name='sample-condition-view'),
    path('sample-conditions/<str:uid>', SampleConditionView.as_view(), name='sample-condition-one'),

    path('sample-nature', SampleNatureView.as_view(), name='sample-nature-view'),
    path('sample-nature/<str:uid>', SampleNatureView.as_view(), name='sample-nature-one'),

    # Fridge Endpoints
    path('fridges', FridgeView.as_view(), name='fridge-view'),
    path('fridges/<str:uid>', FridgeView.as_view(), name='fridge-one'),

    # Fridge Block Endpoints
    path('fridges/<str:fridge_uid>/blocks', FridgeBlockView.as_view(), name='fridge-block-view'),
    path('fridges/<str:fridge_uid>/blocks/<str:block_uid>', FridgeBlockView.as_view(), name='fridge-block-one'),

    # Fridge Partition Endpoints
    path('fridges/<str:fridge_uid>/blocks/<str:block_uid>/partitions', FridgePartitionView.as_view(), name='fridge-partition-view'),
    path('fridges/<str:fridge_uid>/blocks/<str:block_uid>/partitions/<str:partition_uid>', FridgePartitionView.as_view(), name='fridge-partition-one'),
]
