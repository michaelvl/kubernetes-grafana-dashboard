import os, sys
import string
from grafanalib.core import *

sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
from common import *


nodes_num = number('Nodes',
                   [('sum(kube_node_info)')])

pods_running = number('PODs Running',
                      [('sum(kube_pod_status_phase{exported_namespace=~"$namespace", phase="Running"})')])

pods_pending = number('PODs Pending',
                      [('sum(kube_pod_status_phase{exported_namespace=~"$namespace", phase="Pending"})')])

pods_restarting = number('PODs Failed',
                         [('sum(kube_pod_status_phase{exported_namespace=~"$namespace", phase="Failed"})')],
                         thresholds="1,2", colorValue=True)

container_mem_usage = capacity_graph('Container Memory Usage',
                                     [('container_memory_working_set_bytes{container!="",namespace=~"$namespace"}', '{{container}}')])

mem_requests = capacity_graph('Memory Requests Ratio',
                              [('container_memory_working_set_bytes{container!="",namespace=~"$namespace"} / on (container,pod) group_left sum(kube_pod_container_resource_requests{resource="memory",exported_namespace=~"$namespace"}) by (container,pod)', '{{container}}')])

mem_limits = capacity_graph('Memory Limits Ratio',
                            [('container_memory_working_set_bytes{container!="",namespace=~"$namespace"} / on (container,pod) group_left sum(kube_pod_container_resource_limits{resource="memory",exported_namespace=~"$namespace"}) by (container,pod)', '{{container}}')])

cpu_capacity = capacity_graph('Cluster CPU Requests',
                              [('sum(kube_node_status_capacity{resource="cpu",exported_node=~"$node"})', 'allocatable'),
                               ('sum(kube_node_status_allocatable{resource="cpu",exported_node=~"$node"})', 'capacity'),
                               ('sum(kube_pod_container_resource_requests{resource="cpu",exported_node=~"$node"})', 'current')])

mem_capacity = capacity_graph('Cluster Memory Requests',
                              [('sum(kube_node_status_allocatable{resource="memory",exported_node=~"$node"})', 'allocatable'),
                               ('sum(kube_node_status_capacity{resource="memory",exported_node=~"$node"})', 'capacity'),
                               ('sum(kube_pod_container_resource_requests{resource="memory",exported_node=~"$node"})', 'current')])


dashboard = Dashboard(
    title='Resource Usage',
    #editable=False,
    templating = Templating(list=[
        Template(name='node', dataSource=datasource, query='label_values(kubernetes_io_hostname)', includeAll=True, allValue='.*'),
        Template(name='namespace', dataSource=datasource, query='label_values(namespace)', includeAll=True, allValue='.*'),
    ]),
    rows = [
        Row(title='Cluster Overview', collapse=False,
            panels = [
                nodes_num, pods_running, pods_pending, pods_restarting
        ]),
        Row(title='Cluster Resources', collapse=False,
            panels = [
                cpu_capacity, mem_capacity
        ]),
        Row(title='POD Resources', collapse=False,
            panels = [
                mem_requests, mem_limits, container_mem_usage
        ]),
    ],
).auto_panel_ids()
