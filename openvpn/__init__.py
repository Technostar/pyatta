import os
import subprocess

#absolute path os easy-rsa directory
ovpn_config_dir='/etc/openvpn/easy-rsa/'
#this list contains all name of scripts used for generation RSA keys and certificates. The order of this list's item must be concerved
rsa_scripts=['vars','clean-all','build-ca','build-key-server','build-key','build-dh']

class EasyRSAScriptNotFound(Exception): pass
class RSAKeyGenerationFailed(Exception): pass
class CannotInitEnvVariables(Exception): pass
class CannotRemoveExistKeys(Exception): pass
class RSACAKeyGenerationFailed(Exception): pass
class RSAServerKeyGenerationFailed(Exception): pass
class RSAClientKeyGenerationFailed(Exception): pass
class DHParamsGenerationFailed(Exception): pass


def _run(cmd, output=False):
    '''
    To run command and scripts easier
    '''
    if output:
        try:
            out = subprocess.check_output('{}'.format(cmd), shell=True)
        except subprocess.CalledProcessError:
            out = False
        return out
    return subprocess.check_call('{}'.format(cmd), shell=True)


def check_easy_rsa_scripts(root='/etc/openvpn/easy-rsa'):
    '''
    Check if all RSA scripts exist to be able to generate all keys and certificates
    '''
    for file in rsa_scripts:
        if not os.path.isfile(os.path.join(root,file)): raise EasyRSAScriptNotFound('{1} not exist in {0} folder'.format(root, file))

def exec_rsa_scripts(ovpn_server_name='vyatta', ovpn_client_name='client'):
    '''
    Execute RSA script and test if one fails
    '''
    if os.path.isdir(ovpn_config_dir):
        #Initialise environment variable. Needed by OpenSSL
        cmd = 'bash {0}'.format(os.path.join(ovpn_config_dir, 'vars'))
        if _run(cmd, output=False): raise CannotInitEnvVariables('Cannot initialize environment variables')
        cmd = 'bash {0}'.format(os.path.join(ovpn_config_dir, 'clean-all'))
        if _run(cmd, output=False): raise CannotRemoveExistKeys('Cannot remove exist RSA keys')
        cmd = 'bash {0} --batch'.format(os.path.join(ovpn_config_dir, 'build-ca'))
        if _run(cmd, output=False): raise RSACAKeyGenerationFailed('Failed to generate CA key/cert')
        cmd = 'bash {0} --batch --server {1}'.format(os.path.join(ovpn_config_dir, 'build-key-server'), ovpn_server_name)
        if _run(cmd, output=False): raise RSAServerKeyGenerationFailed('Failed to generate server key/cert')
        cmd = 'bash {0} --batch {1}'.format(os.path.join(ovpn_config_dir, 'build-key'), ovpn_client_name)
        if _run(cmd, output=False): raise RSAClientKeyGenerationFailed('Failed to generate client key/cert')
        cmd = 'bash {0}'.format(os.path.join(ovpn_config_dir,'build-dh'))
        if _run(cmd, output=False): raise DHParamsGenerationFailed('Failed to generate DH parameters')
        return True
    return False
