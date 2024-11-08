import collections

CredentialPlugin = collections.namedtuple('CredentialPlugin', ['name', 'inputs', 'backend'])

from jwt import JWT, jwk_from_pem
from urllib.parse import urljoin
import time
import requests
from jwt import JWT, jwk_from_pem

def read_key(path):
    try:
        with open(path, 'rb') as pem_file:
            return jwk_from_pem(pem_file.read())
    except Exception as e:
        raise ValueError("Error while parsing key file: {0}".format(e))

def encode_jwt(jwk, jwt_expiry, org, team, bound_issuer, aud):
    jwt_instance = JWT()
    now = int(time.time())
    payload = {
        'iat': now,
        'exp': now + jwt_expiry,
        'org': org,
        'team': team,
        'sub': 'sub',
        'bound_issuer': bound_issuer,
        'aud': aud
    }
    try:
        return jwt_instance.encode(payload, jwk, alg='RS256')
    except Exception as e:
        raise ValueError("Error while encoding jwt: {0}".format(e))

def gen_jwt(**kwargs):
    org = kwargs.get('org')
    team = kwargs.get('team')
    key_path = kwargs.get('key_path')
    jwt_expiry = kwargs.get('jwt_expiry')
    bound_issuer = kwargs.get('bound_issuer')
    vault_url = kwargs.get('vault_url')

    jwk = read_key(key_path)
    workload_jwt = encode_jwt(jwk, jwt_expiry, org, team, bound_issuer, vault_url)

    try:
        return workload_jwt
    except Exception as e:
        raise RuntimeError(f'Could not generate jwt.')

def vault_jwt_login(**kwargs):
    tower_jwt_role = kwargs['tower_jwt_role']
    jwt = kwargs['jwt']
    vault_jwt_path = kwargs['vault_jwt_path']

    vault_url = urljoin(kwargs['vault_url'], 'v1')
    data = {'role': tower_jwt_role, 'jwt': jwt}
    sess = requests.Session()
    request_url = '/'.join([vault_url, 'auth', vault_jwt_path, 'login'])

    resp = sess.post(request_url, json=data, timeout=30, verify=False)
    resp.raise_for_status()
    token = resp.json()['auth']['client_token']

    return token


def gen_wrapped_secret_id(**kwargs):
    org = kwargs.get('org')
    team = kwargs.get('team')
    team_vault_approle = kwargs.get('team_vault_approle')
    tower_jwt_role = kwargs.get('tower_jwt_role')
    key_path = kwargs.get('key_path')
    jwt_expiry = int(kwargs.get('jwt_expiry'))
    wrap_ttl = kwargs.get('wrap_ttl')
    vault_url = kwargs.get('vault_url')
    bound_issuer = kwargs.get('bound_issuer')
    vault_jwt_path = kwargs.get('vault_jwt_path')
    vault_approle_path = kwargs.get('vault_approle_path')

    jwt = gen_jwt(org=org, team=team, team_vault_approle=team_vault_approle, key_path=key_path, jwt_expiry=jwt_expiry,bound_issuer=bound_issuer, vault_url=vault_url)
    token = vault_jwt_login(tower_jwt_role=tower_jwt_role, jwt=jwt, vault_url=vault_url, vault_jwt_path=vault_jwt_path)

    vault_url = urljoin(vault_url, 'v1')
    request_kwargs = {'timeout': 30, 'verify': 'False'}
    sess = requests.Session()
    sess.headers['Authorization'] = 'Bearer {}'.format(token)
    # Compatibility header for older installs of Hashicorp Vault
    sess.headers['X-Vault-Token'] = token
    sess.headers['X-Vault-Wrap-Ttl'] = wrap_ttl
    request_url = '/'.join([vault_url, 'auth', vault_approle_path, 'role', team_vault_approle, 'secret-id'])

    resp = sess.post(request_url, timeout=30, verify=False)
    resp.raise_for_status()
    wrapped_vault_token = resp.json()['wrap_info']['token']
    return wrapped_vault_token


hashivault_jwt_credential_plugin = CredentialPlugin(
    'HashiVault Wrapped SecretID',

    inputs={
       'fields': [{
            'id': 'vault_url',
            'label': 'Vault URL',
            'type': 'string',
            'format': 'url',
            'help_text': 'Url for the vault instance. e.x. https://vault.company.com'
        }, {
            'id': 'key_path',
            'label': 'Signing Cert Path',
            'type': 'string',
            'help_text': 'Full path to the key/certificate on the controller nodes that is used to sign the JWT.'
        }, {
            'id': 'jwt_expiry',
            'label': 'JWT Expiry',
            'type': 'string',
            'help_text': 'JWT TTL in seconds. e.x. 300'
        }, {
            'id': 'bound_issuer',
            'label': 'Bound Issuer',
            'type': 'string',
            'help_text': 'The issuing identity for the JWT tokens. E.x. https://ansible.tower.com/'
        }, {
            'id': 'wrap_ttl',
            'label': 'Wrap TTL',
            'type': 'string',
            'help_text': 'TTL For the wrapped token in seconds. E.x. 300s'
        }, {
            'id': 'tower_jwt_role',
            'label': 'Tower Vault JWT Role',
            'type': 'string',
            'help_text': 'Name of the Tower\'s Vault JWT Role'
        }, {
            'id': 'vault_jwt_path',
            'label': 'Vault JWT Auth path',
            'type': 'string',
            'default': 'jwt',
            'help_text': 'The name/path of the JWT auth method\'s mount in vault. Defaults to \'jwt\''
        }, {
            'id': 'vault_approle_path',
            'label': 'Vault AppRole Auth path',
            'type': 'string',
            'default': 'approle',
            'help_text': 'The name/path of the AppRole auth method\'s mount in vault. Defaults to \'approle\''
        }],
        'metadata': [{
            'id': 'team',
            'label': 'Team Name',
            'type': 'string',
            'help_text': 'Team name is added to the bound claims of the JWT.'
        },{
            'id': 'org',
            'label': 'Org Name',
            'type': 'string',
            'help_text': 'Org name is added to the bound claims of the JWT.'
        },{
            'id': 'team_vault_approle',
            'label': 'Team Vault AppRole Name',
            'type': 'string',
            'help_text': ''
        }],
        'required': ['key_path', 'expiry'],
    },

    backend = gen_wrapped_secret_id
)