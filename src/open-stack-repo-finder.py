
from __future__ import print_function
import time
import giteapy
from giteapy.rest import ApiException
from pprint import pprint

# Configure API key authorization: AccessToken
configuration = giteapy.Configuration()
# configuration.api_key['access_token'] = 'log6307e'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
configuration.api_key_prefix['access_token'] = 'Bearer'
# Configure API key authorization: AuthorizationHeaderToken
# configuration = giteapy.Configuration()
# configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'
# Configure HTTP basic authorization: BasicAuth
# configuration = giteapy.Configuration()
# configuration.username = 'YOUR_USERNAME'
# configuration.password = 'YOUR_PASSWORD'
# # Configure API key authorization: SudoHeader
# configuration = giteapy.Configuration()
# configuration.api_key['Sudo'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Sudo'] = 'Bearer'
# Configure API key authorization: SudoParam
# configuration = giteapy.Configuration()
# configuration.api_key['sudo'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['sudo'] = 'Bearer'
# Configure API key authorization: Token
# configuration = giteapy.Configuration()
# configuration.api_key['token'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['token'] = 'Bearer'

# create an instance of the API class
repo_api_instance = giteapy.RepositoryApi(giteapy.ApiClient(configuration))
username = 'thomtrep' # str | username of the user that will own the created organization
organization = giteapy.CreateOrgOption(username=username) # CreateOrgOption |

try:
    # Create an organization
    api_response = repo_api_instance.repo_search()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AdminApi->admin_create_org: %s\n" % e)