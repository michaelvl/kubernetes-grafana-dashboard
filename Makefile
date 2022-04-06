IMAGE=ghcr.io/michaelvl/grafanalib@sha256:5fdb3ce6598cd4da6798f146c82afb8c3a2a670539b59190c515455ba8ae3505

.PHONY: render
render:
	docker run --rm -it -v ${PWD}/dashboards:/hosttmp --name grafanalib -e DASHBOARD_DATASOURCE="prometheus" -e DASHBOARD_TITLE="Kubernetes Health Dashboard" ${IMAGE} find /hosttmp/ -name 'dashboard-*.py' -type f -printf '%p\n' -exec sh -c "generate-dashboard -o /hosttmp/\$$(basename {} .py).json {}" {} \;

.PHONY: create-configmap
create-configmap:
	find dashboards -name 'dashboard-*.json' -type f -printf '%p\n' -exec sh -c "kubectl create configmap dashboard --from-file {} --dry-run=client -o yaml | sed \"s/^metadata:/metadata:\n  labels:\n    grafana_dashboard: '1'/\" > \$$(basename {} .json).yaml" {} \;
