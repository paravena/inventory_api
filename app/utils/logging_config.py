import logging
import json
from datetime import datetime
from flask import request
from time import time
from functools import wraps

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        if hasattr(record, 'request_data'):
            log_obj.update(record.request_data)
        return json.dumps(log_obj)

def setup_logger():
    logger = logging.getLogger('inventory_api')
    logger.setLevel(logging.INFO)

    # Create console handler with JSON formatter
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)

    return logger

logger = setup_logger()

def log_endpoint(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time()

        # Capture request details before processing
        request_data = {
            "method": request.method,
            "path": request.path,
            "remote_addr": request.remote_addr,
            "user_agent": request.headers.get('User-Agent'),
        }

        try:
            response = f(*args, **kwargs)
            # Handle different response types
            if isinstance(response, tuple):
                status_code = response[1]
            elif hasattr(response, 'status_code'):
                status_code = response.status_code
            else:
                status_code = 200  # Default status code for successful responses
        except Exception as e:
            logger.error(str(e), extra={
                "request_data": {
                    **request_data,
                    "status_code": 500,
                    "duration_ms": int((time() - start_time) * 1000)
                }
            })
            raise

        duration_ms = int((time() - start_time) * 1000)

        # Log after request is processed
        logger.info(
            f"Endpoint {request.method} {request.path}",
            extra={
                "request_data": {
                    **request_data,
                    "status_code": status_code,
                    "duration_ms": duration_ms
                }
            }
        )

        return response

    return decorated_function
