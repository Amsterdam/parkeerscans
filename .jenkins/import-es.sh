# load database into elastic search.

# NOTE:
#
# We assumes the all database work is ready
# and workspace is still ready and waiting.

set -e
set -u

DIR="$(dirname $0)"

echo $0

dcdb() {
	docker-compose -p pp -f ${DIR}/docker-compose.yml $*;
}


dc() {
	docker-compose -p pp -f ${DIR}/docker-compose-es.yml $*;
}


# remove dockers from elastic import on exit
trap 'dc kill ; dc rm -f -v' EXIT
# remove dockers from database run on exit
trap 'dcdb kill ; dc rm -f -v' EXIT


dc up -d elasticsearch

dc run --rm logstash
dc run --rm el-backup

dc down
