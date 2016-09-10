from django.conf.urls import url
from pipeline.views import create_buildpipeline
from pipeline.views import build_buildpipeline
from pipeline.views import get_buildpipeline_status
from pipeline.views import get_one_buildpipeline_info
from pipeline.views import get_buildpipelines_list
from pipeline.views import get_builds_list
from pipeline.views import get_build_info
from pipeline.views import del_buildpipeline
from pipeline.views import check
from pipeline.views import delByID


urlpatterns = [
    url(r'^v1/buildPipeline$', create_buildpipeline),
    url(r'^v1/buildPipeline/build',build_buildpipeline),
    url(r'^v1/buildPipeline/(.+)/status$',get_buildpipeline_status),
    url(r'^v1/buildPipeLine/(.+)$',get_one_buildpipeline_info),
    url(r'^v1/buildPipeLine$',get_buildpipelines_list),
    url(r'^v1/buildHistory/(.+)$',get_builds_list),
    url(r'^v1/buildPipeline/(.+)/build/(.+)$', get_build_info),
    url(r'^v1/buildPipeLine/(.+)$', del_buildpipeline),
    url(r'^v1/check$',check),
    url(r'delete$',delByID),
]