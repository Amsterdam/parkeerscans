# load database into elastic search.

# NOTE:
#
# We assumes the all database work is ready
# and workspace is still ready and waiting.

set -e
set -u

DIR="$(dirname $0)"

echo $0

dc() {
	docker-compose -p pp -f ${DIR}/docker-compose-es.yml $*;
}

dc up -d elasticsearch

dc run --rm logstash
dc up el-backup

dc stop
