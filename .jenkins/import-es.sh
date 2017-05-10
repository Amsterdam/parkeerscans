# load database into elastic search.

# NOTE assumes the all database work is ready

set -e
set -u

dc() {
	docker-compose -p pp -f ${DIR}/docker-compose.yml $*;
}


dc run --rm logstash
dc up el-backup
