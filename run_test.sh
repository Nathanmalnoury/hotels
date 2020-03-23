BASE_DIR=$(dirname "$0")
cd "$BASE_DIR" || exit
. ./venv/bin/activate
flake8 ./hotels ./tests --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 ./hotels ./tests --count --max-complexity=10 --max-line-length=127 --statistics
pydocstyle ./hotels ./tests --ignore=D2,D107,D105
coverage run --source="./hotels" -m unittest discover
coverage report --fail-under=50 --omit='*/venv/*','*/tests/*','*__.py',
deactivate