#!/usr/bin/python

from flask import Flask, request, jsonify, make_response
import sys
import json
import vyatta


def init_env():
    '''
    Initialize the environment with some params
    '''
    #not yet implemented

app = Flask(__name__)

#Handling standard 404 error
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error':'Ressource not found'}), 404)

@app.route('/shutdown', methods = ['POST'])
def shutdown_server():
    '''
    This function is for shutting down the flask web server
    '''
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Pyatta API shutting down...'

@app.route('/api/v1.0/vyatta/intrefaces/<string:type>', methods=['GET'])
def get_vyatta_ifaces(type):
    try:
        output = vyatta.get_interfaces_infos(type)
    except vyatta.ErrorInterafaceType:
        output = {'error':'Network interface type not recognized'}
    return json.dumps(output)

@app.route('/api/v1.0/vyatta/interfaces/openvpn/', methods=['POST'])
def create_ovpn_iface():
    vyatta.create_ovpn_interface()

if __name__ == "__main__":

    vyatta.create_ovpn_interface()
    #if sys.argv:
        #Starting server
        #try:
            #if sys.argv[1] == 'start': app.run(host='0.0.0.0', debug = True)
        #except IndexError:
            #print "Server not started ! App is in debug mode"
