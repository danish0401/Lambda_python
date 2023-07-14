import json
import logging
import time
import traceback
import requests
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
def lambda_handler(event, context):
  try:
    LOGGER.info('Event structure: %s', event)
    response = requests.get('https://ifconfig.co/json')
    return {
        'statusCode': 200,
        'body': "{}".format(
            response.text
        )
    }
  except Exception as e:
    traceback.print_exc()
    response_data = {
        'statusCode': 500,
        'error': str(e)
    }
    return response_data