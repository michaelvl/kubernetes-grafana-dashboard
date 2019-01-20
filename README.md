A Helm chart for deploying a code-based Kubernetes Grafana dashboard. 

If you think that storing Grafana dashboards .JSON files in git feels like
storing a disassembled binary instead of source code, look no further.

This chart allows dashboards to be defined using Python with the assistance of
[Grafanalib](https://github.com/weaveworks/grafanalib) for propagating the
dashbaords to Grafana.

Defining dashboards with code have a number of benefits:

- Better readability, compact code instead of redundant .JSON.

- Understandable diffs when commited to git, i.e. since the dashboards are code,
  the diffs will look like normal code diffs.  Loading, editing and saving
  Grafana .JSON files could potentially create huge changes in the .JSON file.

- Easy editing using a text editor. Also, since many individual gauges are
  identical, it is easy to build functions to create these and thus reduce the
  amount of boilerplate enormously.

- Configurable dashboards based on e.g. chart values. The example dashboard
  illustrates this with a configurable dashboard title.

See the dashboards folder for an example dashboard, and note that the Grafana
.JSON files are not part of the chart and only exists temporarily while the
Kubernetes job defined by this chart is executed.

Using Helm for deploying dashboards also allows for Helm workflows to be used
while developing dashboards.  Simply re-apply the chart and you have the
dashboard available in Grafana within seconds.

Note that this requires the sidecar in Grafana for dynamic provisioning of
dashboards are enabled.