from flask import request
from flask_restful import Resource
from openapi_core.shortcuts import RequestValidator
from openapi_core.wrappers.flask import FlaskOpenAPIRequest

from common import utils, errors

from auth import check_extra_claims
from models import TapisAccessToken, TapisRefreshToken

class TokensResource(Resource):
    """
    Work with Tapis Tokens
    """
    def post(self):
        validator = RequestValidator(utils.spec)
        result = validator.validate(FlaskOpenAPIRequest(request))
        if result.errors:
            raise errors.ResourceError(msg=f'Invalid POST data: {result.errors}.')
        validated_body = result.body
        # this raises an exception of the claims are invalid -
        if validated_body.extra_claims:
            check_extra_claims(validated_body.extra_claims)
        access_token = TapisAccessToken(**validated_body)
        refresh_token = None
        if validated_body.generate_refresh_token:
            refresh_token = TapisRefreshToken(**validated_body)
        result = {'access_token': access_token}
        if refresh_token:
            result['refresh_token'] = refresh_token
        return utils.ok(result=result, msg="Token generation successful.")

    def put(self):
        validator = RequestValidator(utils.spec)
        result = validator.validate(FlaskOpenAPIRequest(request))
        if result.errors:
            raise errors.ResourceError(msg=f'Invalid PUT data: {result.errors}.')
