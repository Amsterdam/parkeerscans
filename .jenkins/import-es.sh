# load database into elastic search.

# NOTE:
#
# We assumes the all database work is ready
# and workspace is still ready and waiting.

set -e
set -u
set -x

DIR="$(dirname $0)"

echo $0

dces() {
	docker-compose -p pp -f ${DIR}/docker-compose-es.yml $*;
}

# remove dockers from elastic import on exit
# remove dockers from database run on exit
trap 'dcdb kill ; dc rm -f -v' EXIT
dces rm elasticsearch
dces rm logstash

dces pull

dces up -d elasticsearch

dces run --rm logstash

# make sure elastic has premissions to write the files
dces run --rm elasticsearch chmod -R 777 /tmp/backups

dces run --rm elasticsearch rm -rf /tmp/backups/*

dces run --rm esbackup ./docker-el-backup.sh

# make sure jenkins has premissions to remove the files
dces run --rm elasticsearch chmod -R 777 /tmp/backups

dces logs elasticsearch

#dces down
