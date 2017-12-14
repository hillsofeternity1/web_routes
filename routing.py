from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request
import subprocess
import socket

# Script uses ip utility. Commands using for interacting with ip goes next

_get_custom_tables = '''ip route show table all | grep table | awk '{if($6=="table") {print $NF}}' '''
_get_rules = 'ip rule'
_get_routes_default = 'ip route'
_get_routes_custom = 'ip route show table %s'
_get_ip_a = 'ip a'
_get_reles_custom = "ip rule | grep 'lookup %s'"

_add_gateway_for_table = 'sudo ip route add default via %s table %s'
_del_gateway_for_table = 'sudo ip route del default via %s table %s'
_add_client_to_table = 'sudo ip rule add from %s lookup %s'
_del_client_to_table = 'sudo ip rule del from %s lookup %s'

app = Flask(__name__)

def execute(cmd, raw=False):
    shell = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = shell.communicate()[0]
    # make str from bytes
    string = output.decode()[:-1]
    if len(string) == 0:
        return []
    if raw == False:
        output = string.split('\n')
        return output
    elif raw == True:
        return string

@app.route("/", methods=['POST', 'GET'])
def admin():
    message = ''
    if request.method == 'POST':
        try:
            if (request.form['gateway'] and request.form['number']):
                try:
                    socket.inet_aton(request.form['gateway'])
                    if request.form['action'] == 'Add':
                        output = execute((_add_gateway_for_table %
                            (request.form['gateway'], request.form['number'])))
                    else:
                        output = execute((_del_gateway_for_table %
                            (request.form['gateway'], request.form['number'])))
                    if output != '':
                        message = output
                    else:
                        message = 'Table changed successfully.'
                except socket.error:
                    message = 'Incorrect gateway ip.'
        except:
            pass
        try:
            if (request.form['from'] and request.form['action']):
                try:
                    host = socket.gethostbyname(request.form['from'])
                    if request.form['action'] == 'Add':
                        output = execute((_add_client_to_table %
                            (host, request.form['number'])))
                    else:
                        output = execute((_del_client_to_table %
                            (host, request.form['number'])))
                    if output != '':
                        message = output
                    else:
                        message = 'Rule has been added.'
                except:
                    message = 'Something went wrong.'
        except:
            pass
    routes_custom = {}
    for table in execute(_get_custom_tables):
        routes_custom[table] = []
        for line in execute(_get_routes_custom % table):
            routes_custom[table].append(line)
    rules_custome = {}
    for table in execute(_get_custom_tables):
        rules_custome[table] = []
        for line in execute(_get_reles_custom % table):
            rules_custome[table].append(line)

    return render_template(
        'index.html',
        custom_tables=execute(_get_custom_tables),
        rules=routes_custom,
        routes_default=execute(_get_routes_default),
        ip_a=execute(_get_ip_a),
        rules_custome=rules_custome,
        message=message
    )
if __name__ == '__main__':
    app.run(port=5050)
