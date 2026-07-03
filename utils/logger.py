import logging
import os
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        if log_record.get('asctime'):
            log_record['timestamp'] = log_record.pop('asctime')
        if log_record.get('levelname'):
            log_record['level'] = log_record.pop('levelname')
            
        keys_to_remove = [k for k, v in log_record.items() if v is None or k in ['name', 'taskName']]
        for k in keys_to_remove:
            del log_record[k]

def setup_logger(app):
    """Set up structured JSON logging for the Flask application."""
    log_folder = os.getenv('LOG_FOLDER', '/var/log/blackbox')
    try:
        if not os.path.exists(log_folder):
            os.makedirs(log_folder, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create log folder {log_folder}: {e}")

    # The format string specifies which fields the jsonlogger should extract
    format_str = '%(asctime)s %(levelname)s %(message)s %(event)s %(user_id)s %(team_id)s %(challenge_id)s %(claimed_owner_team_id)s %(ip)s %(container_name)s'
    formatter = CustomJsonFormatter(format_str)

    handlers = []
    
    # File handler
    try:
        log_file = os.path.join(log_folder, 'app.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    except Exception as e:
        print(f"Warning: Could not setup file logging: {e}")

    # Stream handler (stdout)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    handlers.append(stream_handler)

    # Replace existing handlers on app.logger
    app.logger.handlers = []
    for h in handlers:
        app.logger.addHandler(h)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info("JSON structured logging initialized", extra={"event": "logging_init"})
