CURRENT_DIR=$(cd $(dirname $0); pwd)

sleep 1m
cd $CURRENT_DIR
. .venv/bin/activate
python -m entry
