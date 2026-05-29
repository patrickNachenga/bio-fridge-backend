from django.urls import path

from api.modules.fridge import FridgeView
from api.modules.project import ProjectView
from api.modules.sample_type import SampleTypeView
from mpiralive.views import MpiraLiveView

urlpatterns = [
    path('list', MpiraLiveView.as_view(), name='mpira-live-list'),
    path('view/<str:id>', MpiraLiveView.as_view(), name='mpira-live-open'),

]