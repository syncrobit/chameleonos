
import os


PORT = int(os.environ.get('PORT', '8080'))
RESOURCES_PATH = os.environ.get('RESOURCES_PATH', '/usr/share/hotspot-api-server/resources')
HTML_PATH = os.environ.get('HTML_PATH', '/usr/share/hotspot-api-server/html')
TLS_PORT = int(os.environ.get('TLS_PORT', '443'))
TLS_CA = os.environ.get('TLS_CA')
TLS_CERT = os.environ.get('TLS_CERT')
TLS_KEY = os.environ.get('TLS_KEY')
