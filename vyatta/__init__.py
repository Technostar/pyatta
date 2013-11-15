import subprocess
import sys
from itertools import izip
from pyparsing import nestedExpr
import openvpn

class ErrorInterafaceType(Exception): pass
class CannotCreateOVPNInterface(Exception): pass

def _run(cmd, output=False):
    '''
    To run command easier
    '''
    if output:
        try:
            out = subprocess.check_output('{}'.format(cmd), shell=True)
        except subprocess.CalledProcessError:
            out = False
        return out
    return subprocess.check_call('{}'.format(cmd), shell=True)

def dico_format(data):
    '''
    Convert a list to dictionary
    '''
    itr = iter(data)
    return dict(izip(itr,itr))

def get_eth_ifaces(interfaces):
    '''
    Parse 'interfaces' variable to get ethernet interfaces with associated description
    '''
    ethernets = {}
    indices = [i for i,v in enumerate(interfaces) if v == 'ethernet']
    for i in indices:
        ethernets[interfaces[i+1]] = dico_format(interfaces[i+2])
    return ethernets

def ovpn_data_format(data):
    '''
    Formating output of 'data' variable into a dictionary.
    This function is typicaly called to help formatting ovpn interface description.
    '''
    infos = {}
    infos['local-port'] = data[data.index('local-port') + 1]
    infos['mode'] = data[data.index('mode') + 1]
    infos['protocol'] = data[data.index('protocol') + 1]
    indice = [i for i,v in enumerate(data) if v == 'server' and data[i-1] != 'mode']
    infos['server'] = dico_format(data[indice[0] + 1])
    infos['tls'] = dico_format(data[data.index('tls') + 1])
    return infos

def get_ovpn_ifaces(interfaces):
    '''
    Parse 'interfaces' variable to get openvpn interfaces with associated description
    '''
    ovpn = {}
    indices = [i for i,v in enumerate(interfaces) if v == 'openvpn']
    for i in indices:
        ovpn[interfaces[i+1]] = ovpn_data_format(interfaces[i+2])
    return ovpn

def get_interfaces_infos(type='all'):
    '''
    Returns all infos about available interfaces in vyatta router
    '''
    out = _run('vyatta-cfg-wrapper show', output=True)
    data = nestedExpr(opener='{', closer='}').parseString('{'+ out +'}').asList()
    #return desc about ethernet interfaces 
    if type == 'eth':
        return get_eth_ifaces(data[0][1])
    #return desc about openvpn interfaces 
    elif type == 'ovpn':
    #return desc about all interfaces 
        return get_ovpn_ifaces(data[0][1])
    elif type == 'all':
        return dict(get_eth_ifaces(data[0][1]).items() + get_ovpn_ifaces(data[0][1]).items())
    else: raise ErrorInterafaceType('Network interaface type not recognized')

def create_ovpn_interface():
    '''
    Create vtun openvpn interface.
    If the name of openvpn interfaces are not suffixed with 'vtun' string, this function will fail.
    '''
    '''
    #get keys witch are names of ovpn interfaces
    ovpn_ifaces = get_interfaces_infos('ovpn').keys()
    i = len(ovpn_ifaces)
    if i == 0:
        new_name = 'vtun0'
    else:
        last_item = ovpn_ifaces[i-1]
        indice = int(last_item[4:]) + 1
        new_name = '{0}{1}'.format('vtun',indice)
    print _run('vyatta-cfg-wrapper begin', output=True)
    cmd = 'vyatta-cfg-wrapper set interfaces openvpn {}'.format(new_name)
    output = _run(cmd, output=True)
    print _run('vyatta-cfg-wrapper commit', output=True)
    print _run('vyatta-cfg-wrapper save', output=True)
    print _run('vyatta-cfg-wrapper end', output=True)
    if not output:
        return new_name
    else: raise CannotCreateOVPNInterface(output)
    '''
    try:
        #check if all RSA scripts exist
        openvpn.check_easy_rsa_scripts()
    except openvpn.EasyRSAScriptNotFound:
        print "[Error] Check if all RSA Scripts exist"
        return False
    try:
        #generate all keys/certs
        openvpn.exec_rsa_scripts(ovpn_server_name='vyatta', ovpn_client_name='wheezy')
    except openvpn.CannotInitEnvVariables:
        print "[Error] Cannot initialize environment variables"
        return False
    except openvpn.CannotRemoveExistKeys:
        print "[Error] Cannot remove exist RSA keys"
        return False
    except openvpn.RSACAKeyGenerationFailed:
        print "[Error] Failed to generate CA key/cert"
        return False
    except openvpn.RSAServerKeyGenerationFailed:
        print "[Error] Failed to generate server key/cert"
        return False
    except openvpn.RSAClientKeyGenerationFailed:
        print "[Error] Failed to generate client key/cert"
        return False
    except openvpn.DHParamsGenerationFailed:
        print "[Error] Failed to generate DH parameters"
        return False
    #If all goes well
    return True
