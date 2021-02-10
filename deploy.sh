#/bin/bash

cd /root/nti2021-api/
git pull
pip3 install -r requirements.txt
systemctl stop daphne
systemctl daemon-reload
python3 manage.py migrate
python3 manage.py collectstatic
systemctl start daphne
