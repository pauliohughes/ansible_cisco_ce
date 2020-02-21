#!/usr/bin/python



ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---

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
        xapi_path=dict(type='list'),
        xapi_value=dict(type='str'),
        state=dict(type='str', default='present', choices=['present', 'absent'])
    )

    
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    import xows
    import asyncio

    result = dict(
        changed=False,
        original_xapi_value='',
        xapi_value='',
        debug_message=''
    )

    error = False

    async def get_current_config():
        async with xows.XoWSClient(module.params['hostname'], 
                                    username=module.params['username'], 
                                    password=module.params['password']) as client:
            get_result = await client.xGet(module.params['xapi_path'])
            return get_result
    
    async def set_config():
        async with xows.XoWSClient(module.params['hostname'], 
                                    username=module.params['username'], 
                                    password=module.params['password']) as client:
            set_result = await client.xSet(module.params['xapi_path'], desired_xapi_value)
            return set_result

    
    try:
        get_result = asyncio.run(get_current_config())
        
        # If we need to make sure something is absent set the value to nothing in case it's set
        if module.params['state'] == 'absent':
            desired_xapi_value = ""

        # Check if the xapi_value is in int to ensure idempotency will work with the api
        # If we get an int back from the API check if xapi is an int too
        elif isinstance(get_result, int) and module.params['state'] == 'present':
            try:
                desired_xapi_value = int(module.params['xapi_value'])
            except:
                # Its not an int, continue as string
                desired_xapi_value = module.params['xapi_value']
        else:
            desired_xapi_value = module.params['xapi_value']

        # Config  matches
        if desired_xapi_value == get_result:
            result['changed'] = False
            result['xapi_value'] = desired_xapi_value
            result['original_xapi_value'] = get_result
            
        # Config doesn't match so need a change
        else: 
            result['changed'] = True
            result['xapi_value'] = desired_xapi_value
            result['original_xapi_value'] = get_result

        # Make the change if Check mode isn't on
        if not desired_xapi_value == get_result and not module.check_mode:
            
            set_result = asyncio.run(set_config())
            result['debug_message'] = set_result

    except Exception as e:
        error = True
        result['msg'] = "error: %s " % str(e)

        
    
    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    if error:
        module.fail_json(**result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()