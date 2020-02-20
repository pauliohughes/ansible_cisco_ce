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

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        original_xapi_value='',
        xapi_value='',
        debug_message=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)

    
    

    import xows
    import asyncio

    async def get_current_config():
        async with xows.XoWSClient(module.params['hostname'], 
                                    username=module.params['username'], 
                                    password=module.params['password']) as client:
            get_result = await client.xGet(module.params['xapi_path'])
            return get_result

    get_result = asyncio.run(get_current_config())

    # Check if the xapi_value is in int to ensure idempotency will work with the api
    # If we get an int back from the API check if xapi is an int too
    if isinstance(get_result, int):
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
        result['changed'] = True
        result['xapi_value'] = desired_xapi_value
        result['original_xapi_value'] = get_result

        async def set_config():
            async with xows.XoWSClient(module.params['hostname'], 
                                        username=module.params['username'], 
                                        password=module.params['password']) as client:
                set_result = await client.xSet(module.params['xapi_path'], desired_xapi_value)
                return set_result


        set_result = asyncio.run(set_config())
        result['debug_message'] = set_result
    
    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    if module.params['xapi_path'] == 'fail me':
        module.fail_json(msg='You requested this to fail', **result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()