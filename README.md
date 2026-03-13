# Ansible-Playbooks

This repository contains example Ansible playbooks you can use as a starting point.

## Prerequisites

- Ansible installed (`ansible --version`)
- SSH access to target hosts

## Repository structure

- `playbooks/ping.yml` - basic connectivity check against all hosts
- `playbooks/install-nginx.yml` - installs and starts NGINX on Debian/Ubuntu hosts

## Example inventory

Create an inventory file (for example `inventory.ini`):

```ini
[web]
192.168.1.10 ansible_user=ubuntu
192.168.1.11 ansible_user=ubuntu
```

## Running the examples

Run a connectivity check:

```bash
ansible-playbook -i inventory.ini playbooks/ping.yml
```

Install NGINX on web hosts:

```bash
ansible-playbook -i inventory.ini playbooks/install-nginx.yml
```

## Notes

- These playbooks are examples; adjust groups, users, and package names for your environment.
- For privilege escalation, ensure your user can use sudo and include `become: true` where needed.

## CI

- A GitHub Actions workflow runs the Ansible playbooks on pull requests and pushes to `main`.

