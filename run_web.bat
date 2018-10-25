@echo off


START http://localhost:5000/

cd flask
SET FLASK_APP=car_search_run
flask run
cd ..