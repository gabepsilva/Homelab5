

TEMPLATE_ID=900

NET_GW='10.10.0.1'

function create_server() {
    NEW_ID=$1
    VM_NAME=$2
    MAC=$3

    echo
    echo
    echo "RECREATING SERVER: $VM_NAME"
    qm clone $TEMPLATE_ID $NEW_ID --name $VM_NAME #--full
    qm set $NEW_ID --delete ide2
    qm set $NEW_ID --net0 virtio,bridge=vmbr0,firewall=1,macaddr=$MAC,queues=4
    if [[ "$VM_NAME" == *"k8s-node"*"-agpu"* ]]; then
        qm set $NEW_ID --cores 4
        qm set $NEW_ID --memory 8192
        qm resize $NEW_ID scsi0 +150G
        qm set 1007 -hostpci0 0000:c3:00,pcie=1 # Adding GPU
    elif [[ "$VM_NAME" == *"k8s-node"* ]]; then
        qm set $NEW_ID --cpu EPYC
        qm set $NEW_ID --cores 2  # assuming default is 2 cores
        qm set $NEW_ID --memory 4096
        qm resize $NEW_ID scsi0 +30G
    fi
    qm start $NEW_ID
    sleep 1
    echo
    echo
}

function create_onprem_cluster() {

#create_server vmid    vm_name        mac
create_server 1001 'k8s-master1'    'BC:24:11:BA:19:F3'
create_server 1002 'k8s-master2'    'BC:24:11:BA:19:F4'
create_server 1003 'k8s-master3'    'BC:24:11:BA:19:F5'
create_server 1004 'k8s-node1'      'BC:24:11:BA:19:F6'
create_server 1005 'k8s-node2'      'BC:24:11:BA:19:F7'
create_server 1006 'k8s-node3'      'BC:24:11:BA:19:F8'
create_server 1007 'k8s-node4-agpu'  'BC:24:11:BA:19:F9'
}

function destroy_onprem_cluster() {

    for id in 1001 1002 1003 1004 1005 1006 1007
    do
        qm stop $id --skiplock --timeout 0
        qm destroy $id --purge
    done
}


destroy_onprem_cluster
create_onprem_cluster