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

# https://www.envoyproxy.io/docs/envoy/latest/configuration/cluster_manager/cluster_stats
# https://www.envoyproxy.io/docs/envoy/latest/configuration/http_conn_man/stats
# https://www.envoyproxy.io/docs/envoy/latest/configuration/statistics

for ns,title in zip(namespaces, titles):
    envoy_servers_live = number('Servers Live',
                                [('sum(envoy_server_live{{kubernetes_namespace="{}"}})'.format(ns))], thresholds="1,2", colors_reverse=True, colorValue=True)

    envoy_servers_unhealthy = number('Servers Unhealthy',
                                     [('(sum(envoy_cluster_membership_healthy{{kubernetes_namespace="{0}"}})-sum(envoy_cluster_membership_total{{kubernetes_namespace="{0}"}}))'.format(ns))], thresholds="1,2", colorValue=True)

    envoy_conns = capacity_graph('Connections',
                                 [('sum(envoy_http_downstream_cx_active{{kubernetes_namespace="{}"}}) by (envoy_http_conn_manager_prefix)'.format(ns), '{{envoy_http_conn_manager_prefix}}'),
                                 ('sum(envoy_server_parent_connections{{kubernetes_namespace="{}"}})'.format(ns), 'Parent connections')], decimals=0)

    envoy_http_codes = capacity_graph('HTTP codes',
                                 [('sum(rate(envoy_http_downstream_rq_xx{{kubernetes_namespace="{}"}}[5m])) by (envoy_response_code_class)'.format(ns), '{{envoy_response_code_class}}xx')])

    envoy_days_cert_exp = number('Days next certificate expiry',
                                 [('min(envoy_server_days_until_first_cert_expiring{{kubernetes_namespace="{}"}})'.format(ns))], thresholds="5,10", colors_reverse=True, colorValue=True, valueMaps=[{'op':'=', 'value':'null', 'text':'No Certs'},{'op':'=', 'value':'2147483647', 'text':'No Certs'}])
    
    row = Row(title=title+' Health', collapse=False,
              panels = [
                  envoy_servers_live, envoy_servers_unhealthy,
                  envoy_days_cert_exp
              ])
    rows.append(row)
    row = Row(title=title+' Status', collapse=False,
              panels = [
                  envoy_conns, envoy_http_codes
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
