import os, sys
import string
from grafanalib.core import *

sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
from common import *

if 'ENVOY_DASHBOARD_NAMESPACES' in os.environ:
    namespaces=os.environ['ENVOY_DASHBOARD_NAMESPACES'].split(',')
else:
    namespaces=['contour-ext', 'contour-int']

if 'ENVOY_DASHBOARD_NAMESPACES' in os.environ:
    titles=os.environ['ENVOY_DASHBOARD_TITLES'].split(',')
else:
    titles=['External Ingress Envoy', 'Internal Ingress Envoy']

rows = []

for ns,title in zip(namespaces, titles):
    envoy_servers_live = number('Servers Live',
                                [('sum(envoy_server_live{{kubernetes_namespace="{}"}})'.format(ns))], thresholds="1,2", colors_reverse=True, colorValue=True)

    envoy_servers_unhealthy = number('Servers Unhealthy',
                                     [('(sum(envoy_cluster_membership_healthy{{kubernetes_namespace="{0}"}})-sum(envoy_cluster_membership_total{{kubernetes_namespace="{0}"}}))'.format(ns))], thresholds="1,2", colorValue=True)


    envoy_conns = capacity_graph('Connections',
                                 [('sum(envoy_http_downstream_cx_active{{kubernetes_namespace="{}"}}) by (envoy_http_conn_manager_prefix)'.format(ns), '{{envoy_http_conn_manager_prefix}}')], decimals=0)

    
    row = Row(title=title+' Health', collapse=False,
              panels = [
                  envoy_servers_live, envoy_servers_unhealthy
              ])
    rows.append(row)
    row = Row(title=title+' Status', collapse=False,
              panels = [
                  envoy_conns
              ])
    rows.append(row)


dashboard = Dashboard(
    title='Ingress Health',
    #editable=False,
    templating = Templating(list=[
        Template(name='node', dataSource=datasource, query='label_values(kubernetes_io_hostname)', includeAll=True, allValue='.*'),
        Template(name='namespace', dataSource=datasource, query='label_values(namespace)', includeAll=True, allValue='.*'),
        #Template(name='deployment', dataSource=datasource, query='label_values(deployment)', includeAll=True, allValue='.*'),
        #Template(name='daemonset', dataSource=datasource, query='label_values(daemonset)', includeAll=True, allValue='.*'),
        #Template(name='statefulset', dataSource=datasource, query='label_values(statefulset)', includeAll=True, allValue='.*'),
    ]),
    rows = rows
).auto_panel_ids()
