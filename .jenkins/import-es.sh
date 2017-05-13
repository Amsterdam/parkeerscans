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
	docker-compose -p pp -f ${DIR}/docker-compose.yml $*;
}


dc run --rm logstash
dc up el-backup

dc stop
