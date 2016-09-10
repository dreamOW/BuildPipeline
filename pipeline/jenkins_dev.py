import xml_operation
import jenkins
from jenkinsapi.jenkins import Jenkins
import datetime
import rancher_dev


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
    credential = data['credential']
    if credential == '':
        credentialid = ''
    else:
        credentialid = ",credentialsId: '"+credential+"'"

    username = data['username']
    password = data['password']
    image = data['pipelineName'] + ':' + data['username']
    harbor_image = 'registry.chinacloudapp.cn:8080/'+data['username']+'/'+image
    stackname = data['deployStack']
    servicename = data['deployService']
    print data['deployProjectId']
    print data['deployStackId']
    print data['deployServiceId']
    tmp = rancher_dev.get_service_image(data['deployProjectId'],data['deployStackId'],data['deployServiceId'])
    service_image = tmp[7:]
    access_key = data['apiKey'].split(':')[0]
    secret_key = data['apiKey'].split(':')[1]
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

    deploy = '''stage 'DEPLOY'
          sh 'docker login -u ''' + username + ''' -p ''' + password + ''' registry.chinacloudapp.cn:8080'
          sh 'wget -O compose.zip http://54.222.207.126:8081/v1/projects/1a127/environments/1e1/composeconfig?token=sQNAeGgHwuJ8C3BcGzygsHn6kRsAhQ2DnNArsWUS&projectId=1a127'
          sh 'tar -xf compose.zip'
          sh "sed -in-place -e '/'''+servicename+'''/,/stdin_open/s#'''+service_image+'#'+harbor_image+'''#g' docker-compose.yml"
          sh 'rm docker-compose.ymln-place'
          sh 'rancher-compose --project-name ''' + stackname + ''' --url http://54.222.207.126:8081/v1/ --access-key ''' + access_key + ''' --secret-key ''' + secret_key + ''' --verbose up -d --force-upgrade --pull --confirm-upgrade ''' + servicename + ''''
    }'''
    if data['autoDeploy'] :
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
        result = {'buildPipeLineName': jobname, 'status': 'RUNNING'}
        return result
    else:
        color = server.get_job_info(jobname)['color']
        if color == 'red':
            status = 'FAILURE'
            if color == 'blue':
                status = 'SUCCESS'
        else:
            status = 'CREATED'
        result = {'buildPipeLineName': jobname, 'status': status}
        return result


def get_build_status(jobname,buildid):
    server1 = get_server_instance()
    j = server1.get_job(jobname)
    build = j.get_build(buildid)
    flag = build.is_running()
    if flag:
        return 'RUNNING'
    else:
        return build.get_status()


def get_single_buildpipeline_info(jobname):
    server = get_server_instance()
    j = server.get_job(jobname)
    result = {}
    result['buildPipeLineName'] = j.name
    result['status'] = get_job_status(jobname)['status']
    check = j.get_last_build_or_none()
    if check == None:
        result['lasteBuildStatus'] = ""
        result['lasteBuildEndData'] = ""
        result['createData'] = ""
    else:
        result['lasteBuildStatus'] = get_build_status(jobname,j.get_last_build().get_number())
        lasteBuildEndData = datetime.datetime.strftime(
            j.get_last_build().get_timestamp() + j.get_last_build().get_duration(), '%Y-%m-%d %H:%M:%S')
        result['lasteBuildEndData'] = lasteBuildEndData
        createData = datetime.datetime.strftime(j.get_first_build().get_timestamp(), '%Y-%m-%d %H:%M:%S')
        result['createData'] = createData
    result['scmType'] = BuildPipeline.objects.get(project_name=jobname).scm_type
    result['scmUrl'] = BuildPipeline.objects.get(project_name=jobname).scm_type
    result['branch'] = BuildPipeline.objects.get(project_name=jobname).scm_type
    result['imageName'] = BuildPipeline.objects.get(project_name=jobname).scm_type
    result['mirrorType'] = BuildPipeline.objects.get(project_name=jobname).mirror_type
    result['mirroTypeScript'] = BuildPipeline.objects.get(project_name=jobname).mirror_script_type
    result['excute'] = BuildPipeline.objects.get(project_name=jobname).mirror_script
    result['autoDeploy'] = BuildPipeline.objects.get(project_name=jobname).auto_delpoy
    deploy = {'stackName': BuildPipeline.objects.get(project_name=jobname).deploy_stack, 'serverName': BuildPipeline.objects.get(project_name=jobname).deploy_service}
    result['deploy'] = deploy
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
        buildpipeline['buildPipeLineName'] = jobname
        buildpipeline['status'] = get_job_status(jobname)['status']
        check = job.get_last_build_or_none()
        if check == None:
            buildpipeline['lasteBuildStatus'] = ''
            buildpipeline['lasteBuildEndData'] = ''
            buildpipeline['createData'] = ''
        else:
            buildpipeline['lasteBuildStatus'] = get_build_status(jobname, job.get_last_build().get_number())
            last_build_Data = datetime.datetime.strftime(job.get_last_build().get_timestamp()+job.get_last_build().get_duration(), '%Y-%m-%d %H:%M:%S')
            buildpipeline['lasteBuildEndData'] = last_build_Data
            create_data = datetime.datetime.strftime(job.get_first_build().get_timestamp(), '%Y-%m-%d %H:%M:%S')
            buildpipeline['createData'] = create_data
        buildpipeline['scmType'] = BuildPipeline.objects.get(project_name=jobname).scm_type
        buildpipeline['scmUrl'] = BuildPipeline.objects.get(project_name=jobname).scm_url
        buildpipeline['autoDeploy'] = BuildPipeline.objects.get(project_name=jobname).auto_delpoy
        buildpipelines.append(buildpipeline)
        i = i +1
    result['totalNum'] = i
    result['buildPipeLines'] = buildpipelines
    return result


def get_build_list(jobname):
    print jobname
    server1 = get_server_instance()
    j = server1.get_job(jobname)
    build_ids = j.get_build_ids()
    result = {}
    builds = []
    i = 0
    for build_id in build_ids:
        build = {}
        build['buildId'] = build_id
        build['status'] = get_build_status(jobname,build_id)
        check = j.get_last_build_or_none()
        if check == None:
            build['buildStartData'] = ''
            build['buildEndData'] = ''
        else:
            build_start_data = datetime.datetime.strftime(j.get_last_build().get_timestamp(), '%Y-%m-%d %H:%M:%S')
            build['buildStartData'] = build_start_data
            build_end_data = datetime.datetime.strftime(j.get_build(build_id).get_timestamp() + j.get_build(build_id).get_duration(), '%Y-%m-%d %H:%M:%S')
            build['buildEndData'] = build_end_data
        build['result'] = j.get_build(build_id).is_good()
        builds.append(build)
        i = i + 1
    result['totalNum'] = i
    result['buildHistory'] = builds
    return result


def get_build_log(jobname, buildnum):
    server1 = get_server_instance()
    j = server1.get_job(jobname)
    result = {}
    try:
       build_info = j.get_build(buildnum)
    except:
        return "No Such Build"
    else:
        result['buildId'] = buildnum
        result['status'] = get_build_status(jobname,buildnum)
        build_start_data = datetime.datetime.strftime(build_info.get_timestamp(), '%Y-%m-%d %H:%M:%S')
        result['buildStartData'] = build_start_data
        build_end_data = datetime.datetime.strftime(build_info.get_timestamp() + build_info.get_duration(), '%Y-%m-%d %H:%M:%S')
        result['buildEndData'] = build_end_data
        result['result'] = build_info.is_good()
        result['buildLog'] = build_info.get_console()
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