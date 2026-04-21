# ansible_deploy

Ansible Collection for deploying Docker Compose applications from a project
directory to a remote server.

## Role: `sleeping_in_bed.ansible_deploy.compose_app`

Example playbook:

```yaml
---
# 这个 play 负责部署 inventory 里 main_serve 主机组的服务器。
- name: Deploy project
  hosts: main_serve
  # 远端创建目录、安装 rsync、执行 Docker 操作时需要提升权限。
  become: true
  # 这个 role 不依赖系统 facts，关闭后可以少一次远端探测。
  gather_facts: false
  roles:
    # 安装 collection 后，用 namespace.collection.role 的格式引用 role。
    - sleeping_in_bed.ansible_deploy.compose_app
```

Example inventory variables:

```yaml
all:
  vars:
    # 本地项目根目录；通常 ansible 目录在项目根目录下，所以取 playbook_dir 的上一级。
    deploy_project_src: "{{ playbook_dir | dirname }}"
    # 远端部署目录；项目文件、compose.yml、Dockerfile、合并后的 .env 都会放到这里。
    deploy_dir: "/opt/deploy/example_app"
    # 要合并并上传的环境变量文件；srcs 按顺序合并，后面的同名变量由 Docker Compose 解析时覆盖前面的值。
    deploy_env_files:
      - srcs: [".env", ".env.prod"]
        # 合并后的目标路径；相对路径会放到 deploy_dir 下。
        dst: ".env"
    # 从本地项目复制到远端部署目录的额外文件，常用来把业务 compose/Dockerfile 映射成标准文件名。
    deploy_extra_files:
      - src: "docker/app_compose.yml"
        # 相对路径会放到 deploy_dir 下；这里会生成远端的 compose.yml。
        dst: "compose.yml"
      - src: "docker/app_Dockerfile"
        # 这里会生成远端的 Dockerfile，供 compose build 使用。
        dst: "Dockerfile"
  children:
    # playbook 里的 hosts: main_serve 会匹配这个主机组。
    main_serve:
      hosts:
        host1:
          # 远端服务器地址。
          ansible_host: 127.0.0.1
          # SSH 登录用户。
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
  # 从 GitHub HTTPS 地址安装 collection；public 仓库不需要 SSH 私钥。
  - name: https://github.com/sleeping-in-bed/ansible_deploy.git
    # 声明这个依赖来自 Git 仓库，而不是 Ansible Galaxy 包名。
    type: git
    # 固定到验证过的版本，避免 main 分支变化影响部署。
    version: v0.1.1
```
