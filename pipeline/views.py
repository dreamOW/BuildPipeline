from django.http import HttpResponse
import jenkins_dev
import json
from models import BuildPipeline


def exist(project_name,username):
    try:
       bb = BuildPipeline.objects.get(username=username,project_name=project_name)
    except:
        return False
    else:
        return True


def create_buildpipeline(request):
    print 'create_buildpipeline'
    if request.method == 'POST':
        print request.body
        data = json.loads(request.body)
        print data
        if exist(data['username'], data['pipelineName']):
            return HttpResponse('exist')
        else:
            buildpipeline = BuildPipeline()
            buildpipeline.project_name = data['pipelineName']
            buildpipeline.scm_type = data['scmType']
            buildpipeline.scm_url = data['scmUrl']
            buildpipeline.scm_branch = data['scmBranch']
            buildpipeline.credential = data['scmCredential']
            buildpipeline.mirror_type = data['mirrorType']
            buildpipeline.mirror_script_type = data['mirrorScriptType']
            buildpipeline.mirror_script = data['mirrorScript']
            buildpipeline.auto_delpoy = data['autoDeploy']
            buildpipeline.deploy_stack = data['deployStackName']
            buildpipeline.deploy_stack_id = data['deployStackId']
            print 'in  there'
            buildpipeline.deploy_service = data['deployServiceName']
            buildpipeline.deploy_service_id = data['deployServiceId']
            buildpipeline.deploy_project = data['deployProjectName']
            buildpipeline.deploy_project_id = data['deployProjectId']
            print 'in there'
            buildpipeline.username = data['username']
            buildpipeline.password = data['password']
            buildpipeline.api_key = data['apikey']
            buildpipeline.save()
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


def build_buildpipeline(request,param1):
    print 'build_buildpipeline'
    if request.method == 'POST':
        try:
            jenkins_dev.build_job(param1)
            print 'in there'
            result = {'buildPipelineName': param1, 'status': 'building', 'result': 'SUCCESS','log':''}
            return HttpResponse(json.dumps(result), content_type="application/json")
        except:
            result = {'result': 'FAILURE'}
            return HttpResponse(json.dumps(result), content_type="application/json")
    else:
        return HttpResponse('method error')


def get_buildpipeline_status(request,param1):
    print 'get_buildpipeline_status'
    if request.method == 'GET':
        name = param1
        result = jenkins_dev.get_job_status(name)
        return HttpResponse(json.dumps(result), content_type="application/json")
    else:
        return HttpResponse('method error')


def get_one_buildpipeline_info(request,param1):
    print 'get_one_buildpipeline_info'
    if request.method == 'GET':
        name = param1
        print name
        result = jenkins_dev.get_single_buildpipeline_info(name)
        return HttpResponse(json.dumps(result), content_type="application/json")
    else:
        return HttpResponse('method error')


def get_buildpipelines_list(request):
    print 'get_buildpipelines_list'
    if request.method == 'GET':
        list = jenkins_dev.get_job_list()
        return HttpResponse(json.dumps(list), content_type="application/json")
    else:
        return HttpResponse('method error')


def get_builds_list(request,param1):
    print 'get_builds_list'
    if request.method == 'GET':
        print param1
        list = jenkins_dev.get_build_list(param1)
        return HttpResponse(json.dumps(list), content_type="application/json")
    else:
        return HttpResponse('method error')


def get_build_info(request,param1,param2):
    print 'get_build_info'
    if request.method == 'GET':
        jobname = param1
        buildnum = param2
        print jobname
        print buildnum
        info = jenkins_dev.get_build_log(jobname, buildnum)
        return HttpResponse(json.dumps(info), content_type="application/json")
    else:
        return HttpResponse('method error')


def del_buildpipeline(request, param1):
    print 'del_buildpipeline'
    if request.method == 'DELETE':
        jenkins_dev.delete_job(param1)
        b = BuildPipeline.objects.get(project_name=param1)
        b.delete()
        result ={'buildPipeline': param1, 'status': 'deleted'}
        return HttpResponse(json.dumps(result), content_type="application/json")
    else:
        return HttpResponse('method error')


def check(request):
    if request.method == 'GET':
        result = {'version': 'v1'}
        return HttpResponse(json.dumps(result), content_type="application/json")
    else:
        return HttpResponse('method error')


def delByID(request):
  b = BuildPipeline.objects.all()
  b.delete()
  return HttpResponse('OK')


def query(request):
  b = BuildPipeline.objects.all()
  for a in b:
      print a.project_name+'   '+a.username
  return HttpResponse("OK")