
import json
import httplib2 as http
import time
# For Python 3
from urllib.parse import urlparse, urlencode

class HttpWrapper():
  
  def __init__(self, uri):
    self.uri = uri
  
  def request(self, path, method, query, body):
    response, content = http.Http().request(
      urlparse(self.uri + path + '?' + urlencode(query)).geturl(), # URL
      method,
      body,
      { 'Accept': 'application/json' } # Header
    )

    # TODO(totoro): Find workaround better than this...
    time.sleep(1)

    if response['status'] != '200':
      raise RuntimeError('Request failed:', response['status'])

    return json.loads(content)
    