import traceback

from flask import request
from flask_restful import Resource
from openapi_core.shortcuts import RequestValidator
from openapi_core.wrappers.flask import FlaskOpenAPIRequest

from common import auth, utils, errors

from auth import check_extra_claims
from models import TapisAccessToken, TapisRefreshToken

# get the logger instance -
from common.logs import get_logger
logger = get_logger(__name__)


class TokensResource(Resource):
    """
    Work with Tapis Tokens
    """
    def post(self):
        logger.debug("top of  POST /tokens")
        # try:
        validator = RequestValidator(utils.spec)
        validated = validator.validate(FlaskOpenAPIRequest(request))
        if validated.errors:
            raise errors.ResourceError(msg=f'Invalid POST data: {validated.errors}.')
        validated_body = validated.body
        # this raises an exception of the claims are invalid -
        if hasattr(validated_body, 'extra_claims'):
            check_extra_claims(validated_body.extra_claims)
        token_data = TapisAccessToken.get_derived_values(validated_body)
        access_token = TapisAccessToken(**token_data)
        access_token.sign_token()
        result = {}
        result['access_token'] = access_token.serialize

        # refresh token --
        if hasattr(validated_body, 'generate_refresh_token') and validated_body.generate_refresh_token:
            refresh_token = TokensResource.get_refresh_from_access_token_data(token_data, access_token)
            result['refresh_token'] = refresh_token.serialize
        return utils.ok(result=result, msg="Token generation successful.")
        # except Exception as e:
        #     return utils.ok(result="Got exception", msg=f"{refresh_token.serialize}")
        #     # return utils.ok(result="Got exception", msg=f"Exception: {traceback.format_exc()}")

    def put(self):
        try:
            validator = RequestValidator(utils.spec)
            validated = validator.validate(FlaskOpenAPIRequest(request))
            if validated.errors:
                raise errors.ResourceError(msg=f'Invalid PUT data: {validated.errors}.')
            refresh_token = validated.body.refresh_token
            refresh_token_data = auth.validate_token(refresh_token)
            token_data = refresh_token_data['access_token']
            token_data.pop('token_type')
            token_data['exp'] = TapisAccessToken.compute_exp(token_data['ttl'])
            access_token = TapisAccessToken(**token_data)
            access_token.sign_token()
            refresh_token = TokensResource.get_refresh_from_access_token_data(token_data, access_token)
            result = {'access_token': access_token.serialize,
                      'refres_token': refresh_token.serialize
                      }
            return utils.ok(result=result, msg="Token generation successful.")
        except Exception as e:
            # return utils.ok(result="Got exception", msg=f"{refresh_token.serialize}")
            return utils.ok(result="Got exception", msg=f"Exception: {traceback.format_exc()}")

    @classmethod
    def get_refresh_from_access_token_data(cls, token_data, access_token):
        """
        Generate a refresh token from access token data as a dictionary and the access_token object. 
        :param token_data: dict
        :param access_token: TapisAccessToken
        :return: TapisRefreshToken, signed
        """
        # refresh tokens have all the same attributes as the associated access token (and same values)
        # except that refresh tokens do not have `delegation` and they do have an `access_token` attr:
        token_data.pop('delegation')
        token_data['access_token'] = access_token.claims_to_dict()
        token_data['access_token'].pop('exp')
        # record the requested ttl for the token so that we can use it to generate a token of equal length
        # at refresh
        token_data['access_token']['ttl'] = token_data['ttl']
        refresh_token_data = TapisRefreshToken.get_derived_values(token_data)
        refresh_token = TapisRefreshToken(**refresh_token_data)
        refresh_token.sign_token()
        return refresh_token
