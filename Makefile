.PHONY: validate
validate:
	docker run --rm -it -v ${PWD}/dashboards:/hosttmp --name grafanalib -e DASHBOARD_DATASOURCE="prometheus" -e DASHBOARD_TITLE="Title" michaelvl/grafanalib:git-89d80ba find /hosttmp/ -name 'dashboard-*.py' -type f -printf '%p\n' -exec sh -c "generate-dashboard -o $$(basename $$0 .py).json {}" {} \;

.PHONY: helm-install
helm-install: validate
	helm lint .
	helm upgrade kubernetes-grafana-dashboard . --install

.PHONY: remove
remove:
	helm delete kubernetes-grafana-dashboard --purge
	kubectl delete cm -l heritage=generated-from-code
