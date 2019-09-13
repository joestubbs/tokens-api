import datetime

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import jwt

from common.config import conf
from common.errors import DAOError

from service import tenants, get_tenant_config

# get the logger instance -
from common.logs import get_logger
logger = get_logger(__name__)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = conf.sql_db_url
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class TapisToken(object):
    """
    Tapis tokens are not persisted to the database but are processed in similar ways to other models.
    This class collects common attributes and methods for both access and refresh tokens.
    """
    # header ----
    typ = 'JWT'
    alg = None

    # claims ----
    iss = None
    sub = None
    token_type = None
    tenant_id = None
    username = None
    account_type = None
    exp = None

    def __init__(self, iss, sub, token_type, tenant_id, username, account_type, ttl, exp, extra_claims=None, alg='RS256'):
        # header -----
        self.typ = TapisToken.typ
        self.alg = alg
        if not self.alg == 'RS256':
            raise

        # input metadata ----
        self.ttl = ttl

        # claims -----
        self.iss = iss
        self.sub = sub
        self.token_type = token_type
        self.tenant_id = tenant_id
        self.username = username
        self.account_type = account_type
        self.exp = exp
        self.extra_claims = extra_claims

        # derived attributes
        self.expires_at = str(self.exp)

        # raw jwt ----
        self.jwt = None

    def sign_token(self):
        """
        Sign the token using the private key associated with the tenant.
        :return:
        """
        tenant = get_tenant_config(self.tenant_id)
        private_key = tenant['private_key']
        self.jwt = jwt.encode(self.claims_to_dict(), private_key, algorithm=self.alg)
        return self.jwt

    @classmethod
    def compute_exp(cls, ttl):
        """
        Compute the exp claim from an input ttl.
        :param ttl:
        :return:
        """
        return datetime.datetime.utcnow() + datetime.timedelta(seconds=ttl)

    @classmethod
    def compute_sub(cls, tenant_id, username):
        """
        Compute the sub claim from input tenant_id and username .
        :param ttl:
        :return:
        """
        return f'{tenant_id}@{username}'

    @property
    def serialize(self):
        return {
            f'{self.token_type}_token': self.jwt.decode('utf-8'),
            'expires_in': self.ttl,
            'expires_at': self.expires_at
        }


class TapisAccessToken(TapisToken):
    """
    Adds attributes and methods specific to access tokens.
    """
    delegation = None
    # these are the standard Tapis access token claims and cannot appear in the extra_claims parameter -
    standard_tapis_access_claims = ('iss', 'sub', 'tenant', 'username', 'account_type', 'exp')

    def __init__(self, iss, sub, tenant_id, username, account_type, ttl, exp, delegation, extra_claims=None):
        super().__init__(iss, sub, 'access', tenant_id, username, account_type, ttl, exp, extra_claims)
        self.delegation = delegation

    def claims_to_dict(self):
        """
        Returns a dictionary of claims.
        :return:
        """
        d = {
            'iss': self.iss,
            'sub': self.sub,
            'tenant_id': self.tenant_id,
            'token_type': self.token_type,
            'delegation': self.delegation,
            'username': self.username,
            'account_type': self.account_type,
            'exp': self.exp,
        }
        if self.extra_claims:
            d.update(self.extra_claims)
        return d


    @classmethod
    def get_derived_values(cls, data):
        """
        Computes derived values for the access token from input and defaults.
        :param data:
        :return:
        """
        # convert required fields to their data model attributes -
        try:
            result = {'tenant_id': data.token_tenant_id,
                      'username': data.token_username,
                      'account_type': data.token_type,
                      }
        except KeyError as e:
            logger.error(f"Missing required token attribute; KeyError: {e}")
            raise DAOError("Missing required token attribute.")

        # compute the subject from the parts
        result['sub'] = TapisToken.compute_sub(result['tenant_id'], result['username'])
        tenant = get_tenant_config(result['tenant_id'])
        # derive the issuer from the associated config for the tenant.
        result['iss'] = tenant['iss']

        # compute optional fields -
        access_token_ttl = getattr(data, 'access_token_ttl', None)
        if not access_token_ttl:
            access_token_ttl = tenant['access_token_ttl']
        result['ttl'] = access_token_ttl
        result['exp'] = TapisToken.compute_exp(access_token_ttl)

        delegation = getattr(data, 'delegation_token', False)
        result['delegation'] = delegation
        return result


class TapisRefreshToken(TapisToken):
    """
    Adds attributes and methods specific to refresh tokens.
    """
    access_token = None

    def __init__(self, iss, sub, tenant_id, username, account_type, ttl, exp, access_token):
        super().__init__(iss, sub, 'refresh', tenant_id, username, account_type, ttl, exp, None)
        self.access_token = access_token


    @classmethod
    def get_derived_values(cls, data):
        result = data
        refresh_token_ttl = result.get('refresh_token_ttl', None)
        if not refresh_token_ttl:
            tenant = get_tenant_config(result['tenant_id'])
            refresh_token_ttl = tenant['refresh_token_ttl']
        result['ttl'] = refresh_token_ttl
        result['exp'] = TapisToken.compute_exp(refresh_token_ttl)
        return result

    def claims_to_dict(self):
        """
        Returns a dictionary of claims.
        :return:
        """
        d = {
            'iss': self.iss,
            'sub': self.sub,
            'tenant_id': self.tenant_id,
            'token_type': self.token_type,
            'username': self.username,
            'account_type': self.account_type,
            'exp': self.exp,
            'access_token': self.access_token
        }
        return d
