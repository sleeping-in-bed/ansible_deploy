# ansible_deploy

Ansible Collection for deploying Docker Compose applications from a project
directory to a remote server.

## Role: `sleeping_in_bed.ansible_deploy.compose_app`

Example playbook:

```yaml
---
# This play deploys the hosts in the main_serve inventory group.
- name: Deploy project
  hosts: main_serve
  # Remote directory creation, rsync installation, and Docker operations need privilege escalation.
  become: true
  # This role does not need facts, so disabling fact gathering avoids an extra remote probe.
  gather_facts: false
  roles:
    # After installing the collection, reference the role as namespace.collection.role.
    - sleeping_in_bed.ansible_deploy.compose_app
```

Example inventory variables:

```yaml
all:
  vars:
    # Local project root. Usually the ansible directory is under the project root, so this uses playbook_dir's parent.
    deploy_project_src: "{{ playbook_dir | dirname }}"
    # Remote deploy directory. Project files, compose.yml, Dockerfile, and the merged .env are placed here.
    deploy_dir: "/opt/deploy/example_app"
    # Environment files to merge and upload. srcs are merged in order; Docker Compose resolves duplicate keys later.
    deploy_env_files:
      - srcs: [".env", ".env.prod"]
        # Destination path for the merged file. Relative paths are placed under deploy_dir.
        dst: ".env"
    # Extra files copied from the local project to the remote deploy directory.
    deploy_extra_files:
      - src: "docker/app_compose.yml"
        # Relative paths are placed under deploy_dir. This creates the remote compose.yml.
        dst: "compose.yml"
      - src: "docker/app_Dockerfile"
        # This creates the remote Dockerfile used by compose build.
        dst: "Dockerfile"
  children:
    # The playbook's hosts: main_serve matches this inventory group.
    main_serve:
      hosts:
        host1:
          # Remote server address.
          ansible_host: 127.0.0.1
          # SSH login user.
          ansible_user: root
```

Install from Git:

```bash
# Public GitHub repositories can use HTTPS without a GitHub SSH key.
ansible-galaxy collection install https://github.com/sleeping-in-bed/ansible_deploy.git -p ansible/collections
```

Or through `requirements.yml`:

```yaml
---
collections:
  # Install the collection from GitHub over HTTPS. Public repositories do not need a GitHub SSH key.
  - name: https://github.com/sleeping-in-bed/ansible_deploy.git
    # This dependency comes from a Git repository, not an Ansible Galaxy collection name.
    type: git
    # Pin a verified version so main branch changes do not affect deployments.
    version: v0.1.1
```
