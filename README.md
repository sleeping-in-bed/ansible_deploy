# ansible_deploy

Ansible Collection for deploying Docker Compose applications from a project
directory to a remote server.

## Role: `sleeping_in_bed.ansible_deploy.compose_app`

Example playbook:

```yaml
---
- name: Deploy project
  hosts: main_serve
  become: true
  gather_facts: false
  roles:
    - sleeping_in_bed.ansible_deploy.compose_app
```

Example inventory variables:

```yaml
all:
  vars:
    deploy_project_src: "{{ playbook_dir | dirname }}"
    deploy_dir: "/opt/deploy/example_app"
    deploy_env_files:
      - srcs: [".env", ".env.prod"]
        dst: ".env"
    deploy_extra_files:
      - src: "docker/app_compose.yml"
        dst: "compose.yml"
      - src: "docker/app_Dockerfile"
        dst: "Dockerfile"
  children:
    main_serve:
      hosts:
        host1:
          ansible_host: 127.0.0.1
          ansible_user: root
```

Install from Git:

```bash
ansible-galaxy collection install git@github.com:sleeping-in-bed/ansible_deploy.git -p ansible/collections
```

Or through `requirements.yml`:

```yaml
collections:
  - name: git@github.com:sleeping-in-bed/ansible_deploy.git
    type: git
    version: v0.1.1
```
