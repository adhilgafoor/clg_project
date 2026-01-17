echo "BUILD START"
python3 -m pip install -r requirements.txt
echo "PIP FINISHED"
# python3 manage.py makemigrations --noinput
# python3 manage.py migrate --noinput
# echo "MIGRATIONS FINISHED"
python3 manage.py collectstatic --noinput --clear
echo "BUILD END"
