import os
import string
from grafanalib.core import *

datasource = os.environ['DASHBOARD_DATASOURCE']

refIds = list(string.ascii_uppercase)

def percentage_gauge(title, exprs, sparkline=True, span=3):
    return SingleStat(
        title=title,
        dataSource=datasource,
        targets=[
            Target(expr=exprs[ii], refId=refIds[ii]) for ii in range(len(exprs))],
        format = PERCENT_UNIT_FORMAT,
        sparkline = SparkLine(show=sparkline),
        thresholds = '80,90',
        valueName = 'current',
        gauge = Gauge(show=True, thresholdMarkers=True),
        span = span
    )

def number(title, exprs, sparkline=True, span=3):
    return SingleStat(
        title=title,
        dataSource=datasource,
        targets=[
            Target(expr=exprs[ii], refId=refIds[ii]) for ii in range(len(exprs))],
        format = NO_FORMAT,
        sparkline = SparkLine(show=sparkline),
        span = span
    )

def capacity_graph(title, exprs):
    return Graph(
        title=title,
        dataSource=datasource,
        targets=[
            Target(expr=exprs[ii][0], legendFormat=exprs[ii][1], refId=refIds[ii]) for ii in range(len(exprs))],
        yAxes=single_y_axis(format=SHORT_FORMAT),
        # alert = Alert(
        #     name='POD Usage Alert',
        #     message="High POD usage",
        #     alertConditions=[
        #         AlertCondition(
        #             Target(
        #                 refId='D',
        #             ),
        #             timeRange=TimeRange("5m", "now"),
        #             evaluator=GreaterThan(0.80),
        #             operator=OP_AND,
        #             reducerType=RTYPE_AVG,
        #         ),
        #     ],
        # ),
    span = 3
    )

pod_usage = percentage_gauge('POD Usage',
                             ['sum(kube_pod_info{node=~"$node",kubernetes_namespace=~"$namespace"}) / sum(kube_node_status_allocatable_pods{node=~".*",kubernetes_namespace=~"$namespace"})'])

cpu_requests = percentage_gauge('CPU Requests',
                                ['sum(kube_pod_container_resource_requests_cpu_cores{node=~"$node",kubernetes_namespace=~"$namespace"}) / sum(kube_node_status_allocatable_cpu_cores{node=~"$node",kubernetes_namespace=~"$namespace"})'])

mem_requests = percentage_gauge('Memory Requests',
                                ['sum(kube_pod_container_resource_requests_memory_bytes{node=~"$node",kubernetes_namespace=~"$namespace"}) / sum(kube_node_status_allocatable_memory_bytes{node=~"$node",kubernetes_namespace=~"$namespace"})'])


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


pods_running = number('PODs Running',
                      [('sum(kube_pod_status_phase{namespace=~"$namespace", phase="Running"})')], span=2)

pods_pending = number('PODs Pending',
                      [('sum(kube_pod_status_phase{namespace=~"$namespace", phase="Pending"})')], span=2)

pods_restarting = number('PODs Failed',
                      [('sum(kube_pod_status_phase{namespace=~"$namespace", phase="Failed"})')], span=2)

pods_succeeded = number('PODs Succeeded',
                      [('sum(kube_pod_status_phase{namespace=~"$namespace", phase="Succeeded"})')], span=2)

pods_unknown = number('PODs Status Unknown',
                      [('sum(kube_pod_status_phase{namespace=~"$namespace", phase="Unknown"})')], span=2)


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
        Row(title='PODs', collapse=False,
            panels = [
                pods_running, pods_pending, pods_restarting, pods_succeeded, pods_unknown
        ]),
    ],
).auto_panel_ids()
