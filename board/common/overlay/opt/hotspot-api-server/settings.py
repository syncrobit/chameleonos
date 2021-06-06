
import os


PORT = int(os.environ.get('PORT', '8080'))
RESOURCES_PATH = os.environ.get('RESOURCES_PATH', '/usr/share/hotspot-api-server/resources')
HTML_PATH = os.environ.get('HTML_PATH', '/usr/share/hotspot-api-server/html')
