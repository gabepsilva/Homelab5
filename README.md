# Kubernetes Cluster Setup with Ansible


## Create the Proxmox template
1. run `cluster/proxmox/golden_image_creation.sh` (can copy and paster in the Proxmox node shell)
2. Manually finish the Ubuntu installation
  - use `ubuntu` as user 
  - set your password

```bash
cd cluster/ansible
ansible-playbook -i inventory_onprem.yml playbook_golden_image.yml --ask-pass --ask-become-pass
```

3. In Proxmox, convert this VM to a template with:
```
qm stop <template-id> --skiplock --timeout 0
qm template <template-id>
```


## Create the cluster
1. Create the cluster
2. take note of the template id in proxmox
3. update `TEMPLATE_ID`
4. run `cluster/proxmox/cluster_creation.sh` (can copy and paster in the Proxmox node shell)


## Set the goldem image basics
```bash
ansible-playbook -i inventory_onprem.yml playbook_server_base.yml
```

6. Deploy the K3s cluster:
```bash
# break this to add a node or master without full rebuild - Break into roles instead of large playbooks
ansible-playbook -i inventory_onprem.yml playbook-cluster-provision.yml
```

# Example of Ansible debug mode:

```bash 
ANSIBLE_STDOUT_CALLBACK=debug ansible-playbook -i inventory_onprem.yml playbook-cluster-provision.yml -vv
```


# Example for rolling back VMs snapshots

for id in 1001 1002 1003 1004 1005 1006 1007
do
    qm rollback $id k3s-ready
    qm start $id 
done

