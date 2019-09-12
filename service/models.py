import enum
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from common.config import conf
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
    tenant = None
    username = None
    account_type = None
    exp = None

    def __init__(self, iss, sub, tenant, username, account_type, exp, extra_claims=None, alg='RS256'):
        # header -----
        self.typ = TapisToken.typ
        self.alg = alg
        if not self.alg == 'RS256':
            raise

        # claims -----
        self.iss = iss
        self.sub = sub
        self.tenant = tenant
        self.username = username
        self.account_type = account_type
        self.exp = exp
        self.extra_claims = extra_claims

        # sig -----
        self.sig = sig


class TapisAccessToken(TapisToken):
    """
    Adds attributes and methods specific to access tokens.
    """
    delegation = None
    # these are the standard Tapis access token claims and cannot appear in the extra_claims parameter -
    standard_tapis_access_claims = set('iss', 'sub', 'tenant', 'username', 'account_type', 'exp')

    def __init__(self, iss, sub, tenant, username, account_type, exp, delegation, extra_claims=None):
        super().__init__(iss, sub, tenant, username, account_type, exp, extra_claims)
        self.delegation = delegation


class TapisRefreshToken(TapisToken):
    """
    Adds attributes and methods specific to refresh tokens.
    """
    access_token = None


class LDAPAccountTypes(enum.Enum):
    user = 'user'
    service = 'service'

    def __repr__(self):
        if self.user:
            return 'user'
        return 'service'

    @property
    def serialize(self):
        return str(self)


class LDAPConnection(db.Model):
    __tablename__ = 'ldap_connections'
    id = db.Column(db.Integer, primary_key=True)
    ldap_id = db.Column(db.String(50), unique=True, nullable=False)
    url = db.Column(db.String(2000), unique=False, nullable=False)
    user_dn = db.Column(db.String(200), unique=False, nullable=False)
    bind_dn = db.Column(db.String(200), unique=False, nullable=False)
    bind_credential = db.Column(db.String(200), unique=False, nullable=False)
    account_type = db.Column(db.Enum(LDAPAccountTypes), unique=False, nullable=False)

    @property
    def serialize(self):
        return {
            'ldap_id': self.ldap_id,
            'url': self.url,
            'user_dn': self.user_dn,
            'bind_dn': self.bind_dn,
            'bind_credential': self.bind_credential,
            'account_type': self.account_type.serialize,
        }


