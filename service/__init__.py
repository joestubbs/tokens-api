from common.auth import tenants as ts
from common.config import conf

def add_tenant_private_keys():
    """
    Look up private keys associated with all tenants configured for the token service  and store them on the
    service's `tenants` singleton.
    :return:
    """
    result = []
    for tenant in ts:
        # in dev mode, the tokens service can be configured to not use the security kernel, in which case we must get
        # the private key for a "dev" tenant directly from the service configs:
        if not conf.use_sk:
            tenant['private_key'] = conf.dev_jwt_public_key,
            result.append(tenant)
        else:
            # TODO -- get the PK from the security kernel...
            pass
    return result

tenants = add_tenant_private_keys()