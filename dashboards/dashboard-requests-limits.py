import os, sys
import string
from grafanalib.core import *

sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
from common import *


mem_requests = capacity_graph('Memory Requests',
                              [('sum(container_memory_working_set_bytes{container!="",namespace=~"$namespace"}) by (container,pod) / sum(kube_pod_container_resource_requests{resource="memory",exported_namespace=~"$namespace"}) by (container,pod)', '{{container}}')])

mem_limits = capacity_graph('Memory Limits',
                            [('sum(container_memory_working_set_bytes{container!="",namespace=~"$namespace"}) by (container,pod) / sum(kube_pod_container_resource_limits{resource="memory",exported_namespace=~"$namespace"}) by (container,pod)', '{{container}}')])


dashboard = Dashboard(
    title=os.environ['DASHBOARD_TITLE'],
    #editable=False,
    templating = Templating(list=[
        Template(name='namespace', dataSource=datasource, query='label_values(namespace)', includeAll=True, allValue='.*'),
    ]),
    rows = [
        Row(title='PODs', collapse=False,
            panels = [
                mem_requests, mem_limits
        ]),
    ],
).auto_panel_ids()
