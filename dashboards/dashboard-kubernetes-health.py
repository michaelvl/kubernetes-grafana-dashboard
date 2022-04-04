import os, sys
import string
from grafanalib.core import *

sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
from common import *


pod_usage = percentage_gauge('POD Usage',
                             ['sum(kube_pod_info{node=~"$node",kubernetes_namespace=~"$namespace"}) / sum(kube_node_status_allocatable_pods{node=~".*",kubernetes_namespace=~"$namespace"})'])

cpu_requests = percentage_gauge('CPU Requests',
                                ['sum(kube_pod_container_resource_requests_cpu_cores{node=~"$node",kubernetes_namespace=~"$namespace"}) / sum(kube_node_status_allocatable_cpu_cores{node=~"$node",kubernetes_namespace=~"$namespace"})'])

mem_requests = percentage_gauge('Memory Requests',
                                ['sum(kube_pod_container_resource_requests_memory_bytes{node=~"$node",kubernetes_namespace=~"$namespace"}) / sum(kube_node_status_allocatable_memory_bytes{node=~"$node",kubernetes_namespace=~"$namespace"})'])


apiserver_request_rates = capacity_graph('API Server Request Rate',
                              [('sum(rate(apiserver_request_count[5m])) by (resource)', '{{resource}}')])


# pv_usage = percentage_gauge('Volume Usage',
#                             ['(sum(node_filesystem_size{nodename=~"$node"}) - sum(node_filesystem_free{nodename=~"$node"})) / sum(node_filesystem_size{nodename=~"$node"})'])

node_filesystem = percentage_gauge('Nodes Filesystem Usage',
                                   ['(sum(node_filesystem_size_bytes{nodename=~"$node"}) - sum(node_filesystem_free_bytes{nodename=~"$node"})) / sum(node_filesystem_size_bytes{nodename=~"$node"})'])


pod_capacity = capacity_graph('Cluster POD Capacity',
                              [('sum(kube_node_status_allocatable_pods{node=~\"$node\",kubernetes_namespace=~"$namespace"})', 'allocatable'),
                               ('sum(kube_node_status_capacity_pods{node=~\"$node\",kubernetes_namespace=~"$namespace"})', 'capacity'),
                               ('sum(kube_pod_info{node=~\"$node\",kubernetes_namespace=~"$namespace"})', 'current')])

cpu_capacity = capacity_graph('Cluster CPU Requests',
                              [('sum(kube_node_status_capacity_cpu_cores{node=~"$node",kubernetes_namespace=~"$namespace"})', 'allocatable'),
                               ('sum(kube_node_status_allocatable_cpu_cores{node=~"$node",kubernetes_namespace=~"$namespace"})', 'capacity'),
                               ('sum(kube_pod_container_resource_requests_cpu_cores{node=~"$node",kubernetes_namespace=~"$namespace"})', 'current')])

mem_capacity = capacity_graph('Cluster Memory Requests',
                              [('sum(kube_node_status_allocatable_memory_bytes{node=~"$node",kubernetes_namespace=~"$namespace"})', 'allocatable'),
                               ('sum(kube_node_status_capacity_memory_bytes{node=~"$node",kubernetes_namespace=~"$namespace"})', 'capacity'),
                               ('sum(kube_pod_container_resource_requests_memory_bytes{node=~"$node",kubernetes_namespace=~"$namespace"})', 'current')])

node_filesystem_capacity = capacity_graph('Nodes Filesystem Capacity',
                                          [('sum(node_filesystem_size_bytes{nodename=~"$node"})', 'available'),
                                           ('sum(node_filesystem_size_bytes{nodename=~"$node"}) - sum(node_filesystem_free_bytes{nodename=~"$node"})', 'usage')])


nodes_num = number('Nodes',
                   [('sum(kube_node_info)')])

nodes_num_unavail = number('Nodes unavailable',
                           [('sum(kube_node_info)-sum(kube_node_status_condition{condition="Ready", status="true"})')],
                           thresholds="1,1", colorValue=True)

nodes_num_failed = number('Nodes unshedulable',
                          [('sum(kube_node_spec_unschedulable)')], thresholds="1,1", colorValue=True)

nodes_num_disk_press = number('Nodes w. disk pressure',
                              [('sum(kube_node_status_condition{condition="DiskPressure", status="true"})')],
                              thresholds="1,2", colorValue=True)

nodes_num_mem_press = number('Nodes w. mem pressure',
                             [('sum(kube_node_status_condition{condition="MemoryPressure", status="true"})')],
                             thresholds="1,2", colorValue=True)


pods_running = number('PODs Running',
                      [('sum(kube_pod_status_phase{namespace=~"$namespace", phase="Running"})')])

pods_pending = number('PODs Pending',
                      [('sum(kube_pod_status_phase{namespace=~"$namespace", phase="Pending"})')])

pods_restarting = number('PODs Failed',
                      [('sum(kube_pod_status_phase{namespace=~"$namespace", phase="Failed"})')],
                         thresholds="1,2", colorValue=True)

pods_succeeded = number('PODs Succeeded',
                      [('sum(kube_pod_status_phase{namespace=~"$namespace", phase="Succeeded"})')])

pods_unknown = number('PODs Status Unknown',
                      [('sum(kube_pod_status_phase{namespace=~"$namespace", phase="Unknown"})')],
                      thresholds="1,2", colorValue=True)


container_num = number('Containers',
                       [('sum(kube_pod_container_status_running{namespace=~"$namespace"})')])

container_restarts = number('Container restarts [/hour]',
                            [('sum(delta(kube_pod_container_status_restarts_total{namespace=~"$namespace"}[60m]))')],
                            thresholds="1,2", colorValue=True)


pv_num = number('Persistent volumes',
                      [('sum(kube_persistentvolume_info)')])

pv_avail = number('Unbound persistent volumes',
                  [('sum(kube_persistentvolume_status_phase{phase="Available", namespace=~"$namespace"})')])

pv_pending = number('Pending persistent volumes',
                    [('sum(kube_persistentvolume_status_phase{phase="Pending", namespace=~"$namespace"})')],
                    thresholds="1,2", colorValue=True)

pv_bound = number('Bound persistent volumes',
                  [('sum(kube_persistentvolume_status_phase{phase="Bound", namespace=~"$namespace"})')])

pv_failed = number('Failed persistent volumes',
                    [('sum(kube_persistentvolume_status_phase{phase="Failed", namespace=~"$namespace"})')],
                   thresholds="1,1", colorValue=True)

pv_bytes_req = number('Persistent volumes bytes requested',
                      [('sum(kube_persistentvolumeclaim_resource_requests_storage_bytes{namespace=~"$namespace"})')],
                      format=BYTES_FORMAT)


targets_num = number('Metrics targets',
                      [('count(up)')])
targets_down = number('Metrics targets down',
                      [('1-absent(up==0)')], thresholds="1,2", colorValue=True)


cert_kubelet_expiry_min = number('Next Kubelet Certificate Expiry [days]',
                                 [('(min(kubelet_certificate_manager_client_expiration_seconds) - time())/3600/24')],
                                 thresholds='24,48', colorValue=True, colors_reverse=True, show_sparkline=False)

cert_kubelet_expiry = capacity_graph('Kubelet Certificate Expiry [days]',
                                     [('(kubelet_certificate_manager_client_expiration_seconds{instance=~\"$node\"} - time())/3600/24', '{{instance}}')])


dashboard = Dashboard(
    title=os.environ['DASHBOARD_TITLE'],
    #editable=False,
    templating = Templating(list=[
        Template(name='node', dataSource=datasource, query='label_values(kubernetes_io_hostname)', includeAll=True, allValue='.*'),
        Template(name='namespace', dataSource=datasource, query='label_values(namespace)', includeAll=True, allValue='.*'),
        #Template(name='deployment', dataSource=datasource, query='label_values(deployment)', includeAll=True, allValue='.*'),
        #Template(name='daemonset', dataSource=datasource, query='label_values(daemonset)', includeAll=True, allValue='.*'),
        #Template(name='statefulset', dataSource=datasource, query='label_values(statefulset)', includeAll=True, allValue='.*'),
    ]),
    rows = [
        Row(title='Cluster Capacity', collapse=False,
            panels = [
                pod_usage, cpu_requests, mem_requests, node_filesystem,
                pod_capacity, cpu_capacity, mem_capacity, node_filesystem_capacity
        ]),
        Row(title='Nodes', collapse=False,
            panels = [
                nodes_num, nodes_num_unavail, nodes_num_failed, nodes_num_disk_press, nodes_num_mem_press, cert_kubelet_expiry_min
        ]),
        Row(title='PODs', collapse=False,
            panels = [
                pods_running, pods_pending, pods_succeeded, pods_restarting, pods_unknown
        ]),
        Row(title='Containers', collapse=False,
            panels = [
                container_num, container_restarts
        ]),
        Row(title='Persistent volumes', collapse=False,
            panels = [
                pv_num, pv_bound, pv_avail, pv_pending, pv_failed, pv_bytes_req
        ]),
        Row(title='API Server', collapse=False,
            panels = [
                apiserver_request_rates
        ]),
        Row(title='Metrics', collapse=False,
            panels = [
                targets_num, targets_down
        ]),
        Row(title='Certificates', collapse=False,
            panels = [
                cert_kubelet_expiry
        ]),
    ],
).auto_panel_ids()
