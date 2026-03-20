# Ansible-Playbooks

![Ansible CI](https://github.com/SonicHedghog/Ansible-Playbooks/actions/workflows/ansible-ci.yml/badge.svg)

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

## Bootstrap scripts

The repository includes optional bootstrap scripts for Python and Node.js tooling:

- `scripts/windows/setup-all.ps1` - interactive wrapper that runs both Windows setup scripts
- `scripts/windows/setup-python.ps1` - installs/configures `uv`
- `scripts/windows/setup-node.ps1` - installs/configures `npm`
- `scripts/linux/setup-all.sh` - interactive wrapper that runs both Linux setup scripts
- `scripts/linux/setup-python.sh` - installs/configures `uv`
- `scripts/linux/setup-node.sh` - installs/configures `npm`

Each script supports optional settings for:

- proxy
- certificate bundle path
- base registry/index URL

Windows examples:

```powershell
./scripts/windows/setup-python.ps1 -UvRegistry "https://pypi.org/simple" -Proxy "http://proxy.example:8080" -CertificatePath "C:\certs\corp-ca.pem"
./scripts/windows/setup-node.ps1 -NpmRegistry "https://registry.npmjs.org/" -Proxy "http://proxy.example:8080" -CertificatePath "C:\certs\corp-ca.pem"
```

Linux examples:

```bash
./scripts/linux/setup-python.sh --registry https://pypi.org/simple --proxy http://proxy.example:8080 --cert /etc/ssl/certs/corp-ca.pem
./scripts/linux/setup-node.sh --registry https://registry.npmjs.org/ --proxy http://proxy.example:8080 --cert /etc/ssl/certs/corp-ca.pem
```

Run both setups in one go (interactive prompts for optional values):

```powershell
./scripts/windows/setup-all.ps1
```

```bash
./scripts/linux/setup-all.sh
```

Run wrappers in non-interactive mode:

```powershell
./scripts/windows/setup-all.ps1 -UvRegistry "https://pypi.org/simple" -NpmRegistry "https://registry.npmjs.org/" -Proxy "http://proxy.example:8080" -CertificatePath "C:\certs\corp-ca.pem" -NonInteractive
```

```bash
./scripts/linux/setup-all.sh --uv-registry https://pypi.org/simple --npm-registry https://registry.npmjs.org/ --proxy http://proxy.example:8080 --cert /etc/ssl/certs/corp-ca.pem --non-interactive
```

## Notes

- These playbooks are examples; adjust groups, users, and package names for your environment.
- For privilege escalation, ensure your user can use sudo and include `become: true` where needed.

## CI

- A GitHub Actions workflow runs the Ansible playbooks on pull requests and pushes to `main`.

