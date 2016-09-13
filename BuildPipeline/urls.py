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
from pipeline.views import query


urlpatterns = (
    url(r'^v1/buildPipelines/$', get_buildpipelines_list),#OK
    #url(r'^v1/buildPipeline/(.+)/status$', get_buildpipeline_status),
    url(r'^v1/buildPipeline/$', create_buildpipeline),#OK

    url(r'^v1/buildPipeline/(.+)/build/([0-9]{1,16})/$', get_build_info),
    url(r'^v1/buildPipeline/(.+)/build/$', build_buildpipeline),#OK
    url(r'^v1/buildPipeline/(.+)/builds/$', get_builds_list),
    url(r'^v1/buildPipeline/delete/([A-Za-z0-9]{1,16})/$', del_buildpipeline),
    url(r'^v1/buildPipeline/([A-Za-z0-9]{1,16})/$', get_one_buildpipeline_info),

    url(r'^check/$',check),
    url(r'delete$',delByID),
    url(r'^q$', query),
)