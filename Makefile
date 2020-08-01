
# Creates .env template if nonexistent and shows steps to completes before starting the container
init:
	@python3 ./setup.py

# Starts docker container
run:
	@docker-compose down
	@docker-compose up ${flags} --remove-orphans
# Starts docker container
rund:
	@make run flags="-d"

# Starts docker container
runb:
	@make run flags="--build --force-recreate"

# Starts docker container
runbd:
	@make run flags="--build --force-recreate -d"

# Run a command in the running wttr.in docker container. Requires cmd="XX" and has an optional flags="-f someflag -it"
dexec:
ifeq (${cmd},)
	@echo
	@echo No command entered to run in the wttr.in docker container. RUN: 
	@echo make dexec cmd='COMMAND' flags_optional='-list -of -flags true'
	@exit 1
else
	@docker exec ${flags} wttr.in bash -c "${cmd}"
endif

# Have supervisor reload srv.py, geo-proxy.py andd proxy.py when making core change sin the code
reload:
	@make dexec cmd="supervisorctl reload"

# If changes are made to the supervisor conf file you can use this option. Does not rebuild docker configuration
reread:
	@make dexec cmd="cp /root/app/share/docker/supervisord.conf /etc/supervisor/supervisord.conf"
	@make dexec cmd="supervisorctl reread && supervisorctl reload"

run-srv:
	@make dexec cmd="python /root/app/bin/srv.py" flags="-it"

run-proxy:
	@make dexec cmd="python /root/app/bin/proxy.py" flags="-it"

run-geoproxy:
	@make dexec cmd="python /root/app/bin/geoproxy.py" flags="-it"

srv-log:
	@make dexec cmd="cat /var/log/supervisor/srv-stdout.log"

srv-err:
	@make dexec cmd="cat /var/log/supervisor/srv-stderr.log"

proxy-log:
	@make dexec cmd="cat /var/log/supervisor/proxy-stdout.log"

proxy-err:
	@make dexec cmd="cat /var/log/supervisor/proxy-stderr.log"

geoproxy-log:
	@make dexec cmd="cat /var/log/supervisor/geoproxy-stdout.log"

geoproxy-err:
	@make dexec cmd="cat /var/log/supervisor/geoproxy-stderr.log"