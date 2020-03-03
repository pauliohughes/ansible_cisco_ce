#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '0.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
'''

EXAMPLES = '''

'''

RETURN = '''

'''

from ansible.module_utils.basic import AnsibleModule

def run_module():

    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        hostname=dict(type='str', required=True),
        username=dict(type='str', required=False, default=False),
        password=dict(type='str', required=True, no_log=True),
        validate_certs=dict(type='bool', required=False, default=False),
        websocket=dict(type='bool', required=True)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    # Initilise variables 
    result = dict(
        changed=False,
        original_value='',
        new_value='',
        debug_message=''
    )

    error = False

    from ansible.module_utils.urls import fetch_url
    import xmltodict

    module.params['url_username'] =  module.params['username']
    module.params['url_password'] = module.params['password']
    module.params['force_basic_auth'] = True

    # Textual value of websocket status
    if module.params['websocket']:
        new_websocket_value = "FollowHTTPService"
    else:
        new_websocket_value = "Off"

    try:
        # Get Current config
        websocket_url = "https://" + module.params['hostname'] + "/getxml?location=/configuration/networkservices/websocket"
        get_result, info = fetch_url(module=module, url=websocket_url)

        websocket_value = xmltodict.parse(get_result.read())
        websocket_status = websocket_value['Configuration']['NetworkServices']['Websocket']['#text']

        result['original_value'] = websocket_status
    
        # Config Matches
        if new_websocket_value == websocket_status:
            result['changed'] = False
        # Config needs to be changed
        else:
            result['changed'] = True
            result['new_value'] = new_websocket_value

        # Make required changes
        if not new_websocket_value == websocket_status and not module.check_mode:
            config_url = "https://" + module.params['hostname'] + "/putxml"
            post_data = "<Configuration><NetworkServices><Websocket>" + new_websocket_value + "</Websocket></NetworkServices></Configuration>"
            #post_data = "<Configuration><NetworkServices><Websocket>dsmfhjd</Websocket></NetworkServices></Configuration>"

            post_result, info = fetch_url(module=module, 
                                    url=config_url, 
                                    method="POST", 
                                    data=post_data)

            # Check if successful
            post_result_text = post_result.read()
            post_result_parsed = xmltodict.parse(post_result_text)        
            print(post_result_parsed)
            if not 'Success' in  post_result_parsed['Configuration']:
                # Something went wrong setting the value
                error = True
                result['msg'] = "error: %s " % post_result_text


    except Exception as e:
        error = True
        result['msg'] = "error: %s " % str(e)

    # Exit with an error
    if error:
        module.fail_json(**result)

    # Exit Successfully 
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()