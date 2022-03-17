CALL .\Scripts\activate
set FLASK_APP=server
set FLASK_ENV=development
start http://127.0.0.1:5000/
python -m flask run
cmd /k