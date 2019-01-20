.PHONY: validate
validate:
	docker run --rm -it -v ${PWD}:/hosttmp --name grafanalib -e DASHBOARD_DATASOURCE="prometheus" -e DASHBOARD_TITLE="Title" michaelvl/grafanalib:git-89d80ba generate-dashboard -o /hosttmp/validated-dashboard.json /hosttmp/dashboards/dashboard.py

.PHONY: helm-install
helm-install: validate
	helm lint .
	helm upgrade kubernetes-grafana-dashboard . --install
