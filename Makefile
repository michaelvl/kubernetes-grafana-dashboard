IMAGE=ghcr.io/michaelvl/grafanalib@sha256:5fdb3ce6598cd4da6798f146c82afb8c3a2a670539b59190c515455ba8ae3505

.PHONY: validate
validate:
	#docker run --rm -it -v ${PWD}/dashboards:/hosttmp --name grafanalib -e DASHBOARD_DATASOURCE="prometheus" -e DASHBOARD_TITLE="Kubernetes Health Dashboard" michaelvl/grafanalib:git-20190309-1428-921f605 find /hosttmp/ -name 'dashboard-*.py' -type f -printf '%p\n' -exec sh -c "generate-dashboard -o /hosttmp/\$$(basename {} .py).json {}" {} \;
	docker run --rm -it -v ${PWD}/dashboards:/hosttmp --name grafanalib -e DASHBOARD_DATASOURCE="prometheus" -e DASHBOARD_TITLE="Kubernetes Health Dashboard" ${IMAGE} find /hosttmp/ -name 'dashboard-*.py' -type f -printf '%p\n' -exec sh -c "generate-dashboard -o /hosttmp/\$$(basename {} .py).json {}" {} \;

.PHONY: helm-install
helm-install: validate
	helm lint .
	helm upgrade kubernetes-grafana-dashboard . --install

.PHONY: helm-remove
helm-remove:
	helm delete kubernetes-grafana-dashboard --purge
	kubectl delete cm -l heritage=generated-from-code
