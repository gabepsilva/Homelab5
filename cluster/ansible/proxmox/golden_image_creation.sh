
VM_ID=800


qm stop $VM_ID --skiplock --timeout 0
qm destroy $VM_ID --purge

# Create new VM with ID VM_ID
qm create $VM_ID --name k8s-golden --memory 2048 --cores 2 --sockets 1 --cpu host

# Create and add the disk first
qm set $VM_ID --scsihw virtio-scsi-single


# Add storage devices
qm set $VM_ID --scsi0 'chrysler-fast-nvme1n1:10,iothread=1,cache=none,discard=on'
qm set $VM_ID --ide2 'local:iso/ubuntu-24.04.1-live-server-amd64.iso,media=cdrom'

# Configure networking with multiqueue
qm set $VM_ID --net0 'virtio,bridge=vmbr0,firewall=1,macaddr=bc:24:11:ba:19:f2,queues=4'

# Configure boot order and machine type
qm set $VM_ID --boot 'order=scsi0;ide2;net0'
qm set $VM_ID --machine q35

# Set OS type and enable KVM
qm set $VM_ID --ostype l26
qm set $VM_ID --kvm 1

# Performance optimizations
qm set $VM_ID --agent enabled=1
qm set $VM_ID --balloon 1
qm set $VM_ID --tablet 0
qm set $VM_ID --hotplug disk,network,usb
qm set $VM_ID --cpu host,flags=+aes

# Startup configuration
qm set $VM_ID --onboot 1
qm set $VM_ID --startup order=1

qm start $VM_ID