from common.config import conf

def get_tenants():
    """
    Retrieve the set of tenants that this token service instance is generating tokens for.
    :return:
    """
    return conf.tenants

tenants_strings = get_tenants()

# tenants configs used by the tokens service
tenants = []
# in dev mode, the tokens API can be configured to not use the security kernel, in which case we must get auxiliary
# configuration directly from the service configs:
if not conf.use_sk:
    for tenant in tenants_strings:
        t = {'tenant_id': tenant,
             'iss': conf[f'{tenant}_iss'],
             }
        tenants.append(t)

else:
    # todo -- look up tenants in the tenants API, get the associated parameters (including sk location) and call the
    pass