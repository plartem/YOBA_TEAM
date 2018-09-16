@echo off


START http://127.0.0.1:5000/

cd flask
SET FLASK_APP=car_search_run
flask run
cd ..