BASE_DIR=$(dirname "$0")
cd "$BASE_DIR" || exit
. ./venv/bin/activate
pylama ./hotels ./tests
python -m unittest
pydocstyle ./hotels ./tests
deactivate