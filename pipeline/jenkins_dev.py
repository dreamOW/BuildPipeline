import xml_operation
import jenkins
from jenkinsapi.jenkins import Jenkins
import datetime
import rancher_dev
from models import BuildPipeline


JENKINS_HOST = 'http://127.0.0.1:8080/'
USER_NAME = 'wangzhi'
USER_PWD = 'wad4623831'
CONFIG_LOCATION = "/Users/wangzhi/Documents/PycharmProjects/BuildPipeline/buildpipeline_dev/config.xml"
GIT_URL_NODE = "scm/userRemoteConfigs/hudson.plugins.git.UserRemoteConfig/url"
GIT_BRANCH_NAME = "scm/branches/hudson.plugins.git.BranchSpec/name"
SHELL_COMMAND = "builders/hudson.tasks.Shell/command"
TRIGGER = "publishers/hudson.tasks.BuildTrigger/childProjects"
SCRIPT = "definition/script"


server = jenkins.Jenkins(JENKINS_HOST)


def get_server_instance():
    jenkins_url = JENKINS_HOST
    server1 = Jenkins(jenkins_url)
    return server1


def transfer(str):
    tmp = str.replace('/','\/')
    return tmp


def parse_xml(data):
    server = get_server_instance()
    tree = xml_operation.read_xml(CONFIG_LOCATION)
    text_node = xml_operation.get_node_by_keyvalue(xml_operation.find_nodes(tree, SCRIPT), {})
    scmurl = data['scmUrl']
    scmBranch = data['scmBranch']
    credential = data['scmCredential']
    if credential == '':
        credentialid = ''
    else:
        credentialid = ",credentialsId: '"+credential+"'"

    username = data['username']
    password = data['password']
    image = data['pipelineName'] + ':' + data['username']
    harbor_image = 'registry.chinacloudapp.cn:8080/'+data['username']+'/'+image
    print 'in there'
    access_key = data['apikey'].split(':')[0]
    secret_key = data['apikey'].split(':')[1]
    print 'in there'
    script = '''env.SCM_URL            = "''' + scmurl + '''"
    env.SCM_BRANCH            = "''' + scmBranch + '''"
    node {

      stage 'CHECKOUT'
        git  branch: "${env.SCM_BRANCH}",url: "${env.SCM_URL}"'''+credentialid+'''
        sh 'docker build -t '''+image +''' .'

     stage 'PUBLISH'
          sh 'docker login -u ''' + username + ''' -p ''' + password + ''' registry.chinacloudapp.cn:8080'
          sh 'docker tag '''+image+''' registry.chinacloudapp.cn:8080/''' + username + '''/''' + image + ''''
          sh 'docker push registry.chinacloudapp.cn:8080/''' + username + '''/''' + image+"'"
    if data['autoDeploy'] :
        stackname = data['deployStackName']
        servicename = data['deployServiceName']
        tmp = rancher_dev.get_service_image(data['deployProjectId'], data['deployStackId'], data['deployServiceId'])
        service_image = tmp[7:]
        deploy = '''stage 'DEPLOY'
                  sh 'docker login -u ''' + username + ''' -p ''' + password + ''' registry.chinacloudapp.cn:8080'
                  sh 'wget --http-user=F4245A00346AD0FCC25E  --http-passwd=pGbzmen19VK1WE89so8yh7pSjRULEpQBwSrqgcbx -O compose.zip http://54.222.207.126:8081/v1/projects/''' + \
                 data['deployProjectId'] + '''/environments/''' + data[
                     'deployStackId'] + '''/composeconfig?projectId=''' + data['deployProjectId'] + ''''
                  sh 'tar -xf compose.zip'
                  sh "sed -in-place -e '/''' + servicename + '''/,/stdin_open/s#''' + service_image + '#' + harbor_image + '''#g' docker-compose.yml"
                  sh 'rm docker-compose.ymln-place'
                  sh 'rancher-compose --project-name ''' + stackname + ''' --url http://54.222.207.126:8081/v1/ --access-key ''' + access_key + ''' --secret-key ''' + secret_key + ''' --verbose up -d --force-upgrade --pull --confirm-upgrade ''' + servicename + ''''
            }'''
        temp = script
        script = temp + '\n'+deploy
    else:
        temp = script
        script = temp + '}'
    xml_operation.change_node_text(text_node, script)
    xml_operation.write_xml(tree, CONFIG_LOCATION)
    file_object = open(CONFIG_LOCATION)
    try:
        all_the_text = file_object.read()
    finally:
        file_object.close()
    return all_the_text


def create_job(job_name, config_xml):
    server.create_job(job_name, config_xml)


def parse_xml1(data):
    tree = xml_operation.read_xml(CONFIG_LOCATION)
    if data['mirrorScriptType'] == 0:
        text_node = xml_operation.get_node_by_keyvalue(xml_operation.find_nodes(tree,SCRIPT), {})
        xml_operation.change_node_text(text_node,data["mirrorScript"])
        xml_operation.write_xml(tree, CONFIG_LOCATION)
        file_object = open(CONFIG_LOCATION)
        try:
            all_the_text = file_object.read()
        finally:
            file_object.close()
        return all_the_text


def create_job1(job_name, config_xml):
    server.create_job(job_name, config_xml)


def build_job(job_name):
    build_info = server.build_job(job_name)
    return build_info


def delete_job(job_name):
    server.delete_job(job_name)


def get_job_status(jobname):
    flag = is_build_complete(jobname)
    if flag:
        result = {'buildPipelineName': jobname, 'status': 'building'}
        return result
    else:
        color = server.get_job_info(jobname)['color']
        print color
        if color == 'red':
            status = 'failure'
        elif color == 'blue':
            status = 'success'
        else:
            status = 'created'
        result = {'buildPipelineName': jobname, 'status': status}
        return result


def get_build_status(jobname,buildid):
    server1 = get_server_instance()
    j = server1.get_job(jobname)
    build = j.get_build(buildid)
    flag = build.is_running()
    if flag:
        return 'building'
    else:
        return build.get_status()


def get_single_buildpipeline_info(jobname):
    server1 = get_server_instance()
    j = server1.get_job(jobname)
    result = {}
    result['buildPipelineName'] = j.name
    result['status'] = get_job_status(jobname)['status']
    print result['status']
    check = j.get_last_build_or_none()
    if check is None:
        result['lasteBuildStatus'] = ""
        result['lasteBuildEndDate'] = ""
        result['createData'] = ""
    else:
        result['lasteBuildStatus'] = get_build_status(jobname,j.get_last_build().get_number())
        lasteBuildEndDate = datetime.datetime.strftime(
            j.get_last_build().get_timestamp() + j.get_last_build().get_duration(), '%Y-%m-%d %H:%M:%S')
        result['lasteBuildEndDate'] = lasteBuildEndDate
        createDate = datetime.datetime.strftime(j.get_first_build().get_timestamp(), '%Y-%m-%d %H:%M:%S')
        result['createDate'] = createDate
    print 'in there'
    result['scmType'] = BuildPipeline.objects.get(project_name=jobname).scm_type
    result['scmUrl'] = BuildPipeline.objects.get(project_name=jobname).scm_url
    result['scmBranch'] = BuildPipeline.objects.get(project_name=jobname).scm_branch
    result['imageName'] = j.name+':'+BuildPipeline.objects.get(project_name=jobname).username
    result['mirrorType'] = BuildPipeline.objects.get(project_name=jobname).mirror_type
    result['mirroTypeScript'] = BuildPipeline.objects.get(project_name=jobname).mirror_script_type
    result['mirrorScript'] = BuildPipeline.objects.get(project_name=jobname).mirror_script
    result['autoDeploy'] = BuildPipeline.objects.get(project_name=jobname).auto_delpoy
    result['stackName'] =  BuildPipeline.objects.get(project_name=jobname).deploy_stack
    result['serviceName'] = BuildPipeline.objects.get(project_name=jobname).deploy_service
    return result


def get_job_list():
    server1 = get_server_instance()
    result = {}
    buildpipelines = []
    i = 0
    for j in server1.get_jobs():
        job = server1.get_job(j[0])
        buildpipeline = {}
        jobname = job.name
        buildpipeline['buildPipelineName'] = jobname
        print get_job_status(jobname)['status']
        buildpipeline['status'] = get_job_status(jobname)['status']
        check = job.get_last_build_or_none()
        if check is None:
            buildpipeline['lasteBuildStatus'] = ''
            buildpipeline['lasteBuildEndDate'] = ''
            buildpipeline['createData'] = ''
        else:
            buildpipeline['lasteBuildStatus'] = get_build_status(jobname, job.get_last_build().get_number())
            last_build_Data = datetime.datetime.strftime(job.get_last_build().get_timestamp()+job.get_last_build().get_duration(), '%Y-%m-%d %H:%M:%S')
            buildpipeline['lasteBuildEndDate'] = last_build_Data
            create_data = datetime.datetime.strftime(job.get_first_build().get_timestamp(), '%Y-%m-%d %H:%M:%S')
            buildpipeline['createData'] = create_data
        print 'in there'
        buildpipeline['scmType'] = BuildPipeline.objects.get(project_name=jobname).scm_type
        buildpipeline['scmUrl'] = BuildPipeline.objects.get(project_name=jobname).scm_url
        buildpipeline['autoDeploy'] = BuildPipeline.objects.get(project_name=jobname).auto_delpoy
        print 'in there'
        buildpipelines.append(buildpipeline)
        i = i +1
    result['totalNum'] = i
    print 'in there'
    result['buildPipelines'] = buildpipelines
    return result


def get_build_list(jobname):
    print jobname
    server1 = get_server_instance()
    j = server1.get_job(jobname)
    build_ids = j.get_build_ids()
    print 'in there'
    result = {}
    builds = []
    i = 0
    for build_id in build_ids:
        build = {}
        build['buildPipelineName'] = jobname
        build['buildId'] = build_id
        build['status'] = get_build_status(jobname,build_id)
        check = j.get_last_build_or_none()
        if check is None:
            build['buildStartDate'] = ''
            build['buildEndDate'] = ''
        else:
            build_start_data = datetime.datetime.strftime(j.get_last_build().get_timestamp(), '%Y-%m-%d %H:%M:%S')
            build['buildStartDate'] = build_start_data
            build_end_data = datetime.datetime.strftime(j.get_build(build_id).get_timestamp() + j.get_build(build_id).get_duration(), '%Y-%m-%d %H:%M:%S')
            build['buildEndDate'] = build_end_data
        build['result'] = j.get_build(build_id).is_good()
        builds.append(build)
        i = i + 1
    result['totalNum'] = i
    result['builds'] = builds
    return result


def get_build_log(jobname, buildnum):
    server1 = get_server_instance()
    j = server1.get_job(jobname)
    result = {}
    #try:
    buidldid = int(buildnum)
    build_info = j.get_build(buidldid)
    #except:
        #return "No Such Build"
    #else:
    result['buildPipelineName'] = jobname
    result['buildId'] = buildnum
    result['status'] = get_build_status(jobname, buidldid)
    build_start_data = datetime.datetime.strftime(build_info.get_timestamp(), '%Y-%m-%d %H:%M:%S')
    result['buildStartDate'] = build_start_data
    build_end_data = datetime.datetime.strftime(build_info.get_timestamp() + build_info.get_duration(), '%Y-%m-%d %H:%M:%S')
    result['buildEndDate'] = build_end_data
    result['result'] = build_info.is_good()
    result['log'] = build_info.get_console()
    return result


def is_build_complete(jobname):
    server1 = get_server_instance()
    j = server1.get_job(jobname)
    return j.is_running()


def get_latest_build(jobname):
    status = server.get_job_info(jobname)
    return status['lastCompletedBuild']['number']


def get_job_info(jobname):
    info = server.get_job_info(jobname)
    return info