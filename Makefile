export ROOT_PATH = ${PWD}

init:
	mkdir grafana && sudo chmod a+w grafana
	echo "Initializing..."
	docker-compose up --abort-on-container-exit
	#docker-compose up > /dev/null 2>&1 --abort-on-container-exit
	echo "Done"
