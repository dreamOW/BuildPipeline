from django.http import HttpResponse
import jenkins_dev
import json
from models import BuildPipeline


def exist(project_name,username):
    name = username
    try:
       bb = BuildPipeline.objects.get(username=username,project_name=project_name)
    except:
        return False
    else:
        return True


def create_buildpipeline(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        if exist(data['username'], data['pipelineName']):
            buildpipeline = BuildPipeline()
            buildpipeline.project_name = data['pipelineName']
            buildpipeline.scm_type = data['scmType']
            buildpipeline.scm_url = data['scmUrl']
            buildpipeline.scm_branch = data['scmBranch']
            buildpipeline.credential = data['credential']
            buildpipeline.mirror_type = data['mirrorType']
            buildpipeline.mirror_script_type = data['mirrorScriptType']
            buildpipeline.mirror_script = data['mirrorScript']
            buildpipeline.auto_delpoy = data['autoDeploy']
            buildpipeline.deploy_stack = data['deployStack']
            buildpipeline.deploy_stack_id = data['deployStackId']
            buildpipeline.deploy_service = data['deployService']
            buildpipeline.deploy_service_id = data['deployServiceId']
            buildpipeline.deploy_project = data['deployProject']
            buildpipeline.deploy_project_id = data['deployProjectId']
            buildpipeline.username = data['username']
            buildpipeline.password = data['password']
            buildpipeline.api_key = data['apiKey']
            buildpipeline.save()
        else:
            return HttpResponse('exist')
        if data['mirrorType'] == 0:
            config = jenkins_dev.parse_xml(data)
            print config
            jenkins_dev.create_job(data['pipelineName'],config)
            jenkins_dev.build_job(data['pipelineName'])
            result = {'pipelineName': data['pipelineName'],'status': 'creating'}
            return HttpResponse(json.dumps(result), content_type="application/json")
        else:
            config = jenkins_dev.parse_xml1(data)
            jenkins_dev.create_job1(data['pipelineName'], config)
            jenkins_dev.build_job(data['pipelineName'])
            result = {'pipelineName': data['pipelineName'], 'status': 'creating'}
            return HttpResponse(json.dumps(result), content_type="application/json")
    else:
        return HttpResponse('method error')


def build_buildpipeline(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        jenkins_dev.build_job(data['projectName'])
        result = {'buildPipeLineName': data['projectName'], 'status': 'building', 'result': 'building'}
        return HttpResponse(json.dumps(result), content_type="application/json")
    else:
        return HttpResponse('method error')


def get_buildpipeline_status(request,param1):
    if request.method == 'GET':
        name = param1
        result = jenkins_dev.get_job_status(name)
        return HttpResponse(json.dumps(result), content_type="application/json")
    else:
        return HttpResponse('method error')


def get_one_buildpipeline_info(request,param1):
    if request.method == 'GET':
        name = param1
        result = jenkins_dev.get_single_buildpipeline_info(name)
        return HttpResponse(json.dumps(result), content_type="application/json")
    else:
        return HttpResponse('method error')


def get_buildpipelines_list(request):
    if request.method == 'GET':
        list = jenkins_dev.get_job_list()
        return HttpResponse(json.dumps(list), content_type="application/json")
    else:
        return HttpResponse('method error')


def get_builds_list(request,param1):
    if request.method == 'GET':
        list = jenkins_dev.get_build_list(param1)
        return HttpResponse(json.dumps(list), content_type="application/json")
    else:
        return HttpResponse('method error')


def get_build_info(request,param1,param2):
    if request.method == 'GET':
        jobname = param1
        buildnum = param2
        info = jenkins_dev.get_build_log(jobname, buildnum)
        return HttpResponse(json.dumps(info), content_type="application/json")
    else:
        return HttpResponse('method error')


def del_buildpipeline(request, param1):
    if request.method == 'DELETE':
        jenkins_dev.delete_job(param1)
        result ={'buildPipeLineID': param1, 'status': 'deleted'}
        return HttpResponse(json.dumps(result), content_type="application/json")
    else:
        return HttpResponse('method error')


def check(request):
    if request.method == 'GET':
        result = {'value': 'v1'}
        return HttpResponse(json.dumps(result), content_type="application/json")
    else:
        return HttpResponse('method error')


def delByID(request):
  b = BuildPipeline.objects.all()
  b.delete()
  return HttpResponse('OK')