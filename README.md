# ansible_cisco_ce
Ansible module for Cisco CE Endpoint Configuration

## How to use
- Install pyxows and ansible into the same env
- Run the playbook. e.g ansible-playbook -i hosts.ini example-playbook.yml

## Todo:
- Test Check mode
- Error Handling
- State present/absent
- More to be thought of
- string/int handling for numbers. Numbers always come back as changed e.g 514 to "514"