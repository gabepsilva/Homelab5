# Kubernetes Cluster Setup with Ansible

This repository contains Ansible playbooks for setting up a highly available Kubernetes cluster using Jeff Geerling's Docker and Kubernetes roles.

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

## Directory Structure

```
.
├── README.md
├── inventory.yaml
├── cluster.yaml
└── group_vars/
    ├── k8s_masters.yaml
    └── k8s_nodes.yaml
```

## Installation Steps

1. Clone this repository:
```bash
git clone https://github.com/gabepsilva/Homelab5
cd Homelab5/cluster-provision
```

2. Install required Ansible roles:
```bash
ansible-galaxy install geerlingguy.docker geerlingguy.kubernetes
```

3. Update the inventory file:
- Verify all hostnames are correct
- Adjust the `ansible_user` variable to match your SSH user

4. Verify connectivity to all nodes:
```bash
ansible all -i inventory.yaml -m ping
```

5. Run the playbook:
```bash
ansible-playbook -i inventory.yaml cluster.yaml
```

## Configuration Details

### Docker Configuration
- Docker CE installation
- Docker Compose is disabled by default
- Configured user permissions for the specified ansible_user

### Kubernetes Configuration
- Version: 1.28 (configurable in site.yml)
- CNI Provider: Calico
- Pod Network CIDR: 192.168.0.0/16
- Control plane endpoint: First master node
- Node taints: Control plane nodes are tainted to prevent workload scheduling

## Post-Installation

1. Access the cluster:
```bash
# On the first master node
kubectl get nodes
```

2. Verify cluster health:
```bash
kubectl get pods -A
kubectl get componentstatuses
```

3. Set up kubectl on your local machine:
```bash
# Copy from the first master node
scp root@k8s-master1.i.psilva.org:/etc/kubernetes/admin.conf ~/.kube/config
```

## Load Balancer Setup (TODO)

The cluster is prepared for high availability but requires a load balancer for the control plane. Options include:
- HAProxy
- Nginx
- Cloud load balancer
- MetalLB for bare metal deployments

## Backup Considerations

1. Regular etcd snapshots:
```bash
kubectl exec -n kube-system etcd-k8s-master1 -- etcdctl snapshot save snapshot.db
```

2. Backup important configurations:
- /etc/kubernetes/*
- /var/lib/etcd
- Certificates in /etc/kubernetes/pki

## Maintenance

### Adding New Nodes
1. Add node details to inventory.yml
2. Run the playbook with --limit for the new node:
```bash
ansible-playbook -i inventory.yml site.yml --limit new-node.example.com
```

### Upgrading Kubernetes
1. Update kubernetes_version in site.yml
2. Run the playbook with --tags upgrade:
```bash
ansible-playbook -i inventory.yml site.yml --tags upgrade
```

## Troubleshooting

1. Check node status:
```bash
kubectl get nodes
kubectl describe node <node-name>
```

2. View system logs:
```bash
journalctl -u kubelet
```

3. Check pod status:
```bash
kubectl get pods --all-namespaces
kubectl describe pod <pod-name> -n <namespace>
```

## Security Considerations

1. Network Policies: Consider implementing network policies for pod-to-pod communication
2. RBAC: Set up proper role-based access control
3. Pod Security Policies: Implement pod security policies
4. Regular updates: Keep all components updated
5. API Server access: Restrict API server access to trusted networks

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License

## Contact

For issues and support, please open an issue in the repository.