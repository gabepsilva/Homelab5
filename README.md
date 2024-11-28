# Kubernetes Cluster Setup with Ansible

This repository contains Ansible playbooks for setting up a highly available Kubernetes cluster using K3s, along with essential applications and services.

## Cluster Architecture

- **Control Plane Nodes (Masters):**
  - k8s-master1.i.psilva.org
  - k8s-master2.i.psilva.org
  - k8s-master3.i.psilva.org

- **Worker Nodes:**
  - k8s-node1.i.psilva.org
  - k8s-node2.i.psilva.org
  - k8s-node3.i.psilva.org

## Prerequisites

1. Ubuntu servers for all nodes (tested with Ubuntu 22.04 LTS)
2. SSH access to all servers with sudo privileges
3. Ansible installed on your control machine
4. DNS resolution configured for all hostnames
5. Python 3.x installed on all nodes

## Project Structure

```
.
├── apps/
├── cluster/
│   ├── argocd/
│   ├── cluster-provision-playbook.yml
│   ├── inventory.yml
│   ├── longhorn/
│   └── monitoring/
└── README.md
```

## Installation Steps

1. Clone this repository:
```bash
git clone https://github.com/gabepsilva/HomeLab5
cd HomeLab5
```

2. Update the inventory file:
- Verify all hostnames are correct
- Adjust the `ansible_user` variable to match your SSH user

3. Verify connectivity to all nodes:
```bash
export ANSIBLE_HOST_KEY_CHECKING=False
ansible all -i cluster/inventory.yml -m ping -u gabs
```

4. Deploy the K3s cluster:
```bash
ansible-playbook -i cluster/inventory.yml cluster/playbook-cluster-provision.yml
ansible-playbook -i cluster/inventory.yml cluster/playbook-local-setup.yml
kubectl get nodes
```

5. Deploy ArgoCD:
```bash
# Using password prompt
ansible-playbook -i cluster/inventory.yml cluster/argocd/playbook-deploy-argocd.yml --ask-vault-pass

# Or using a password file
echo "your-vault-password" > ~/.vault_pass
chmod 600 ~/.vault_pass
ansible-playbook -i cluster/inventory.yml cluster/argocd/playbook-deploy-argocd.yml --vault-password-file ~/.vault_pass
```
6. Deploy LongHorn:
```bash
# Using password prompt
ansible-playbook -i cluster/inventory.yml cluster/longhorn/playbook-deploy-longhorn.yml
```

6.5. Restore Longhorn Backups

7. Deploy Monitoring
```bash
ansible-playbook -i cluster/inventory.yml cluster/monitoring/playbook-monitoring-stack.yml --vault-password-file ~/.vault_pass
```

8. Install Jenkins
kubectl apply -f apps/jenkins/argo-application.yaml 



# Access to the management portals

https://argocd.i.psilva.org
http://longhorn.i.psilva.org
http://grafana.i.psilva.org
http://jenkins.i.psilva.org


## Security Considerations

1. Network Policies: Consider implementing network policies for pod-to-pod communication
2. RBAC: Set up proper role-based access control
3. Pod Security Policies: Implement pod security policies
4. Regular updates: Keep all components updated
5. API Server access: Restrict API server access to trusted networks

## Backup Considerations

1. Longhorn volume backups:
- Configure backup targets
- Set up recurring backup schedules
- Test restore procedures

2. Cluster state backup:
- etcd snapshots (managed by K3s)
- Configuration backups
- ArgoCD application definitions

## Troubleshooting

1. Check node status:
```bash
kubectl get nodes
kubectl describe node <node-name>
```

2. View system logs:
```bash
journalctl -u k3s
journalctl -u k3s-agent  # On worker nodes
```

3. Check pod status:
```bash
kubectl get pods --all-namespaces
kubectl describe pod <pod-name> -n <namespace>
```

4. ArgoCD troubleshooting:
```bash
kubectl get applications -n argocd
argocd app get <app-name>
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License

## Contact

For issues and support, please open an issue in the repository.