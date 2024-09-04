from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler
from rest_framework import status

import logging
logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    logger.warning(f"\n\n An error has occured! \n exc: {exc}\n context: {context}\n\n")

    response = exception_handler(exc, context)

    if response is not None:
        # Customize the response for 404 errors
        if response.status_code == status.HTTP_404_NOT_FOUND:
            response.data = {'detail': 'Resource not found.'}

    return response

class InvalidUUIDException(APIException):
    status_code = 404
    default_detail = 'Invalid UUID provided.'
    default_code = 'invalid_uuid'