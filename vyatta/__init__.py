import subprocess
from itertools import izip
from pyparsing import nestedExpr


class NoEthernetInterafaceFound(Exception): pass

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
    itr = iter(data)
    return dict(izip(itr,itr))

def get_eth_ifaces(interfaces):
    ethernets = {}
    indices = [i for i,v in enumerate(interfaces) if v == 'ethernet']
    for i in indices:
        ethernets[interfaces[i+1]] = dico_format(interfaces[i+2])
    return ethernets

def ovpn_data_format(data):
    infos = {}
    infos['local-port'] = data[data.index('local-port') + 1]
    infos['mode'] = data[data.index('mode') + 1]
    infos['protocol'] = data[data.index('protocol') + 1]
    indice = [i for i,v in enumerate(data) if v == 'server' and data[i-1] != 'mode']
    infos['server'] = dico_format(data[indice[0] + 1])
    infos['tls'] = dico_format(data[data.index('tls') + 1])
    return infos

def get_ovpn_ifaces(interfaces):
    ovpn = {}
    indices = [i for i,v in enumerate(interfaces) if v == 'openvpn']
    for i in indices:
        ovpn[interfaces[i+1]] = ovpn_data_format(interfaces[i+2])
    return ovpn

def get_interfaces_infos(type='all'):
    out = _run('vyatta-cfg-wrapper show', output=True)
    data = nestedExpr(opener='{', closer='}').parseString('{'+ out +'}').asList()
    if type == 'eth':
        return get_eth_ifaces(data[0][1])
    elif type == 'ovpn':
        return get_ovpn_ifaces(data[0][1])
    else:
        return dict(get_eth_ifaces(data[0][1]).items() + get_ovpn_ifaces(data[0][1]).items())
