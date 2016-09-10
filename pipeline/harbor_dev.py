import urllib2
import json
import base64
from harborclient import harborclient

USER_NAME = 'admin'
USER_PWD = 'Harbor12345'
AUTH = base64.b64encode(USER_NAME + ':' + USER_PWD)
DEFAULT_HEADER = {'Content-type': 'application/json', 'Accept': 'text/plain', "Authorization": "Basic " + AUTH}
HARBOR_URL = 'http://42.159.231.173:8080'


def project_add_user(username,projectname):
    role = '4'
    url = HARBOR_URL+'/api/projects/'+role+'/members/'
    values = {
        "roles": [
                0
                 ],
        "username": username
    }
    json_data = json.dumps(values)
    req = urllib2.Request(url, json_data,DEFAULT_HEADER)
    response = urllib2.urlopen(req)
    return response.read()