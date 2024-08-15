import collections

CredentialPlugin = collections.namedtuple('CredentialPlugin', ['name', 'inputs', 'backend'])

try:
    from jwt import JWT, jwk_from_pem
    HAS_JWT = True
except ImportError:
    HAS_JWT = False

from datetime import datetime, timedelta, timezone
from jwt import JWT, jwk_from_pem
from jwt.utils import get_int_from_datetime
import time
import json

if HAS_JWT:
    jwt_instance = JWT()
else:
    jwk_from_pem = None
    jwt_instance = None

def read_key(path):
    try:
        with open(path, 'rb') as pem_file:
            return jwk_from_pem(pem_file.read())
    except Exception as e:
        raise ValueError("Error while parsing key file: {0}".format(e))

def encode_jwt(jwk, exp, org, team, vault_role, key_path):
    now = int(time.time())
    payload = {
        'iat': now,
        'exp': now + exp,
        'org': org,
        'team': team,
        'vault_role': vault_role,
    }
    try:
        return jwt_instance.encode(payload, jwk, alg='RS256')
    except Exception as e:
        raise ValueError("Error while encoding jwt: {0}".format(e))

def gen_jwt(**kwargs):

    org = kwargs.get('org')
    team = kwargs.get('team')
    vault_role = kwargs.get('vault_role')
    key_path = kwargs.get('key_path')
    exp = int(kwargs.get('expiry'))

    jwk = read_key(key_path)
    workload_jwt = encode_jwt(jwk, exp, org, team, vault_role, key_path)

    if vault_role:
        try:
            return workload_jwt
        except Exception as e:
            raise RuntimeError(f'Could not generate jwt for {vault_role}.')

hashivault_jwt_credential_plugin = CredentialPlugin(
    'HashiVault JWT Credential',

    inputs={
       'fields': [{
            'id': 'key_path',
            'label': 'Path to the key/certificate on the controller node that is used to sign the JWT.',
            'type': 'string',
        }, {
            'id': 'expiry',
            'label': 'JWT max ttl value in seconds',
            'type': 'string',
        }],
        'metadata': [{
            'id': 'team',
            'label': 'Name of the Team this token will be used by.',
            'type': 'string',
            'help_text': 'Team name is added to the bound claims of the JWT.'
        },{
            'id': 'org',
            'label': 'Name of the org in Tower for this JWT.',
            'type': 'string',
            'help_text': 'Org name is added to the bound claims of the JWT.'            
        },{
            'id': 'vault_role',
            'label': 'Name of the team\'s vault role',
            'type': 'string',
            'help_text': 'The Vault Role is added to the bound claims of the JWT.'            
        }],
        'required': ['key_path', 'expiry'],
    },

    backend = gen_jwt
)

