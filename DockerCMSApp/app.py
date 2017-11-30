from flask import Flask, Response, render_template, request
import json
from subprocess import Popen, PIPE
import os

app = Flask(__name__)

@app.route("/")
def index():
    return """
    Available API endpoints:

    GET /containers                     List all containers
    GET /containers?state=running      List running containers (only)
    GET /containers/<id>                Inspect a specific container
    GET /containers/<id>/logs           Dump specific container logs
    GET /images                         List all images
      
       
    POST /images                        Create a new image
    POST /containers                    Create a new container
        
    PATCH /containers/<id>              Change a container's state
    PATCH /images/<id>                  Change a specific image's attributes
         
    DELETE /containers/<id>             Delete a specific container
    DELETE /containers                  Delete all containers (including running)
    DELETE /images/<id>                 Delete a specific image
    DELETE /images                      Delete all images
    """


def docker(*args):
    cmd = ['docker']
    for sub in args:
        cmd.append(sub)
    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if stderr.startswith(b'Error'):
        print ('Error: {0} -> {1}'.format(' '.join(cmd), stderr))
    return stderr + stdout

# 
# Docker output parsing helpers
#

#
# Parses the output of a Docker PS command to a python List
# 
def docker_ps_to_array(output):
    all = []
    for c in [line.split() for line in output.splitlines()[1:]]:
        each = {}
        each['id'] = c[0].decode('utf-8')
        each['image'] = c[1].decode('utf-8')
        each['name'] = c[-1].decode('utf-8')
        each['ports'] = c[-2].decode('utf-8')
        all.append(each)
    return all

#
# Parses the output of a Docker service ls to a python List
#
def docker_service_ls_to_array(output):
    all = []
    for c in [line.split() for line in output.splitlines()[1:]]:
        each = {}
        each['id'] = c[0].decode('utf-8')
        each['name'] = c[1].decode('utf-8')
        each['mode'] = c[2].decode('utf-8')
        each['replicas'] = c[3].decode('utf-8')
        each['image'] = c[4].decode('utf-8')
        each['ports'] = c[5].decode('utf-8')
        all.append(each)
    return all

#
# Parses the output of Docker node ls to a python List
#
def docker_node_ls_to_array(output):
    all = []
    for c in [line.split() for line in output.splitlines()[1:]]:
        each = {}
        each['id'] = c[0].decode('utf-8')
        each['hostname'] = c[1].decode('utf-8')
        each['status'] = c[2].decode('utf-8')
        each['availability'] = c[3].decode('utf-8')
        all.append(each)
    return all

#
# Parses the output of a Docker logs command to a python Dictionary
# (Key Value Pair object)
def docker_logs_to_object(id, output):
    logs = {}
    logs['id'] = id
    all = []
    for line in output.splitlines():
        all.append(line.decode('utf-8'))
    logs['logs'] = all
    return logs

#
# Parses the output of a Docker image command to a python List
# 
def docker_images_to_array(output):
    all = []
    for c in [line.split() for line in output.splitlines()[1:]]:
        each = {}
        each['id'] = c[2].decode('utf-8')
        each['tag'] = c[1].decode('utf-8')
        each['name'] = c[0].decode('utf-8')
        all.append(each)
    return all


@app.route('/containers', methods=['GET'])
# define an endpoint to list all containers
def conainers_index():
    """
    List all containers
    curl -s -X GET -H 'Accept: application/json'
    http://localhost:8080/containers | python -mjson.tool
    curl -s -X GET -H 'Accept: application/json'
    http://localhost:8080/containers?state=running | python -mjson.tool
    """
    if request.args.get('state') == 'running':
        output = docker('ps')
    else:
        output = docker('ps', '-a')
    resp = json.dumps(docker_ps_to_array(output))
    return Response(response=resp, mimetype="application/json")

@app.route('/containers/<id>', methods=['GET'])
# Endpoint to inspect a specific container
def container_specific(id=None):
    """
    Inspect specific container
    curl -s -X GET -H 'Accept: application/json'
    http://localhost:8080/containers/<id> | python -mjson.tool
    """
    output = docker('container', 'inspect', id)
    resp = json.dumps(output.decode('utf-8'))
    return Response(response=resp, mimetype="application/json")

@app.route('/containers/<id>/logs', methods=['GET'])
# Endpoint to dump specific container logs
def container_logs(id=None):
    """
    Dump specific container logs
    curl -s -X GET -H 'Accept: application/json'
    http://localhost:8080/containers/<id>/logs | python -mjson.tool
    """
    output = docker('container', 'logs', id)
    resp = json.dumps(docker_logs_to_object(id,output))
    return Response(response=resp, mimetype="application/json")

@app.route('/services', methods=['GET'])
#Endpoint to list all services
def services_index():
    """
    List all service
    curl -s -X GET -H 'Accept: application/json'
    http://localhost:8080/services | python -mjson.tool
    """
    output = docker('service', 'ls')
    resp = json.dumps(docker_service_ls_to_array(output))
    return Response(response=resp, mimetype="application/json")

@app.route('/nodes', methods=['GET'])
#Endpoint to list all nodes in the swarm
def nodes_index():
    """
    List all nodes in the swarm
    curl -s -X GET -H 'Accept: application/json'
    http://localhost:8080/nodes | python -mjson.tool
    """
    output = docker('node','ls')
    resp = json.dumps(docker_node_ls_to_array(output))
    return Response(response=resp, mimetype="application/json")

@app.route('/containers', methods=['POST'])
#Endpoint to create a new container
def create_container():
    """
    Create a container

    curl -X POST -H 'Content-Type: application/json'
    http://localhost:8080/containers -d '{"image": "baselm/lab5-image"}'
    curl -X POST -H 'Content-Type: application/json'
    http://localhost:8080/containers -d '{"image": "baselm/lab5-image", "publish": "80:5000"}'
            
    """
    if not request.json or not 'image' in request.json:
        resp = json.dumps("Bad request")
        return Response(response=resp, mimetype="application/json")
    if 'publish' in request.json:
        output = docker('create', '-p', request.json['publish'], request.json['image'])
    else:
        output = docker('create', request.json['image'])
    resp = json.dumps(output.decode('utf-8'))
    return Response(response=resp, mimetype="application/json")

@app.route('/containers/<id>', methods=['PATCH'])
#Endpoint to change a container's state
def change_state_container(id=None):
    """
    Update a container: (Run|pause|stop)
    curl -X PATCH -H 'Content-Type: application/json'
    http://localhost:8080/containers/b6cd8ea512c8 -d '{"state": "run"}'
    curl -X PATCH -H 'Content-Type: application/json'
    http://localhost:8080/containers/b6cd8ea512c8 -d '{"state": "stop"}'

    """
    if not request.json or not 'state' in request.json:
        resp = json.dumps("Bad request")
        return Response(response=resp, mimetype="application/json")

    state = request.json['state']
    if state == 'run':
        output = docker('container', 'start', id)

    if state == 'pause':
        output = docker('container', 'pause', id)

    if state == 'stop':
        output = docker('container', 'stop', id)

    resp = json.dumps(output.decode('utf-8'))
    return Response(response=resp, mimetype="application/json")

@app.route('/containers/<id>', methods=['DELETE'])
#Endpoint to delete a specific container
def delete_container(id=None):
    """
    Delete a specific container:

    curl -s -X DELETE -H 'Accept: application/json'
    http://localhost:8080/containers/<id> | python -mjson.tool
    """
    output = docker('container', 'rm', '-f', id)
    resp = json.dumps(output.decode('utf-8'))
    return Response(response=resp, mimetype="application/json")

@app.route('/containers', methods=['DELETE'])
#Endpoint to delete all the containers
def delete_all_containers():
    """
    Delete all containers:
    curl -s -X DELETE -H 'Accept: application/json'
    http://localhost:8080/containers/ | python -mjson.tool
    """
    ids = docker_ps_to_array(docker('ps', '-a'))
    for aux in ids:
        docker('stop', aux['id'])
        docker('rm', aux['id'])
    resp= json.dumps("All containers deleted!")
    return Response(response=resp, mimetype="application/json")

@app.route('/images', methods=['GET'])
#Endpoint to list all images
def list_images():
    """
    List all iamges:
    curl -s -X GET -H 'Accept: application/json'
    http://localhost:8080/images | python -mjson.tool
    """
    output = docker('images', '-a')
    resp = json.dumps(docker_images_to_array(output))
    return Response(response=resp, mimetype="application/json")

@app.route('/images', methods=['POST'])
#Endpoint to create a new image
def build_image():
    """
    Create image:
    curl -X POST -H 'Content-Type: application/json'
    http://localhost:8080/images -d {"path": "https://github.com/baselm/lab5-init-repo"}'
    """
    if not request.json or not 'path' in request.json:
        resp = json.dumps("Bad request")
        return Response(response=resp, mimetype="application/json")

    if 'tag' in request.json:
        output = docker('image', 'build', '-t', request.json['tag'],'-f', './Dockerfile', request.json['path'])
    else:
        output = docker('image', 'build', request.json['path'])
    resp = json.dumps(output.decode('utf-8'))
    return Response(response=resp, mimetype="application/json")

@app.route('/images/<id>', methods=['PATCH'])
#Endpoint to change a specific image's attributes
def edit_image(id=None):
    """
    Update image attributes:
     curl -s -X PATCH -H 'Content-Type: application/json'
     http://localhost:8080/images/<id> -d '{"tag": "tag1"}'
     
    """
    if not request.json or not 'tag' in request.json:
        resp = json.dumps("Bad request")
    else:
        output = docker('tag', id, request.json['tag'])
        docker('rmi', id)
        resp = json.dumps(output.decode('utf-8'))
    return Response(response=resp, mimetype="application/json")

@app.route('/images/<id>', methods=['DELETE'])
#Endpoint to delete a specific image
def delete_image(id=None):
    """
    Delete a specfic image:
     curl -s -X DELETE -H 'Accept: application/json'
     http://localhost:8080/images/<id> | python -mjson.tool
    """
    output = docker('image', 'rm', '-f', id)
    resp = json.dumps(output.decode('utf-8'))
    return Response(response=resp, mimetype="application/json")

@app.route('/images', methods=['DELETE'])
#Endpoint to delete all images
def delete_images():
    """
    Delete all images:
    curl -s -X DELETE -H 'Accept: application/json'
    http://localhost:8080/images/ | python -mjson.tool
    """
    ids = docker_images_to_array(docker('images', '-a'))
    for aux in ids:
        docker('rmi', '-f', aux['id'])
    resp= json.dumps("All images removed!")
    return Response(response=resp, mimetype="application/json")


if __name__ == "__main__":
    app.run(host='0.0.0.0')
