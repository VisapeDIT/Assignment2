from flask import Flask

app = Flask(__name__)

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

    """
    output = docker('container', 'inspect', id)
    resp = json.dumps(docker_inspect_to_array(output))
    return Response(response=resp, mimetype="application/json")

@app.route('/containers/<id>/logs', methods=['GET'])
# Endpoint to dump specific container logs
def container_logs(id=None):
    """

    """
    output = docker('container', 'logs', id)
    resp = json.dumps(docker_logs_to_array(output))
    return Response(response=resp, mimetype="application/json")

@app.route('/services', methods=['GET'])
#Endpoint to list all services
def services_index():
    """

    """
    output = docker('service', 'ls')
    resp = json.dumps(docker_service_ls_to_array(output))
    return Response(response=resp, mimetype="application/json")

@app.route('/nodes', methods=['GET'])
#Endpoint to list all nodes in the swarm
def nodes_index():
    """

    """
    output = docker('node','ls')
    resp = json.dumps(docker_nodes_ls_to_array(output))
    return Response(response=resp, mimetype="application/json")
