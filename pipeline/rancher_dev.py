import base64
import httplib
import json

RANCHER_HOST = '54.222.207.126:8081'
RANCHER_ACCESS_KEY = 'F4245A00346AD0FCC25E'
RANCHER_SECRET_KEY = 'pGbzmen19VK1WE89so8yh7pSjRULEpQBwSrqgcbx'
AUTH = base64.b64encode(RANCHER_ACCESS_KEY + ':' + RANCHER_SECRET_KEY)
DEFAULT_HEADER = {'Content-type': 'application/json', 'Accept': 'application/json', "Authorization": "Basic " + AUTH}


def get_stackid(stackname):
    httpClient = httplib.HTTPConnection(RANCHER_HOST)
    httpClient.request('GET', 'http://ranchecluster.cloudapp.net:8080/v1/projects/?name='+stackname,
                       '', DEFAULT_HEADER)
    response = httpClient.getresponse()
    data = response.read()
    return data['name']


def create_service(servicename, imagename, stackname):
    conn = httplib.HTTPConnection(RANCHER_HOST)
    params = ({"description": "", "environmentId": "1e83", "name": servicename, "scale": 0,
               "launchConfig": {"imageUuid": imagename}, "secondaryLaunchConfigs": [],
               "assignServiceIpAddress": False})
    stackid = get_stackid(stackname)
    conn.request("POST", "/v1/projects/"+stackid+"/services", json.JSONEncoder().encode(params), DEFAULT_HEADER)
    response = conn.getresponse()
    data = response.read()
    print response.status
    print response.reason
    conn.close()


def get_service_id(service_name):
    httpClient = httplib.HTTPConnection(RANCHER_HOST)
    httpClient.request('GET', 'http://ranchecluster.cloudapp.net:8080/v1/projects/1a8/services/?name='+service_name, '', DEFAULT_HEADER)
    response = httpClient.getresponse()
    data=response.read()
    return data['id']


def get_service_image(environmentid , stackid, serviceid):
    httpClient = httplib.HTTPConnection('54.222.207.126:8081')
    httpClient.request('GET','http://54.222.207.126:8081/v1/projects/'+stackid+'/services/'+serviceid, '', DEFAULT_HEADER)
    response = httpClient.getresponse()
    data=response.read()
    jdata = json.loads(data)
    return jdata['launchConfig']['imageUuid']


def activate_service(service_id):
    conn = httplib.HTTPConnection(RANCHER_HOST)
    params = ({})
    conn.request("POST", "/v1/projects/1a8/services/"+service_id+"/?action=activate", json.JSONEncoder().encode(params), DEFAULT_HEADER)
    response = conn.getresponse()
    data = response.read()
    print response.status
    print response.reason
    conn.close()

def create_stack(stackname):
    conn = httplib.HTTPConnection(RANCHER_HOST)
    params = ({"name": stackname, "dockerCompose": "", "rancherCompose": ""})
    conn.request("POST", "/v1/projects/1a8/environments", json.JSONEncoder().encode(params), DEFAULT_HEADER)
    response = conn.getresponse()
    data = response.read()
    print response.status
    print response.reason
    conn.close()


def create_host():
    conn = httplib.HTTPConnection(RANCHER_HOST)
    params = ({"description": "test", "name": "test"})
    conn.request("POST", "/v1/projects/1a8/registrationTokens", json.JSONEncoder().encode(params), DEFAULT_HEADER)
    response = conn.getresponse()
    data = response.read()
    print response.status
    print response.reason
    conn.close()


def create_containers():
    conn = httplib.HTTPConnection(RANCHER_HOST)
    params = ({ "expose":[], "imageUuid": "docker:ubuntu:14.04.3", "name": "test", "networkIds" :[], "ports": [],
                "startOnCreate": True, "command": [], "publishAllPorts": False, "privileged": False, "capAdd": [],
                "capDrop": [], "dns": [], "dnsSearch": [], "stdinOpen": False, "tty": False, "entryPoint": [],
                "restartPolicy": "", "devices": [], "healthCheck": None, "securityOpt": [], "logConfig": None,
                "extraHosts":[], "readOnly": False, "build": None, "networkMode": "managed", "dataVolumes": [],
                "dataVolumesFrom": []})
    conn.request("POST", "/v1/projects/1a8/containers", json.JSONEncoder().encode(params), DEFAULT_HEADER)
    response = conn.getresponse()
    data = response.read()
    print response.status
    print response.reason
    conn.close()