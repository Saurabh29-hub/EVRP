to run backend server

1. create virtual env 
! python -m venv venv

2. activate venv
! .\venv\Scripts\activate

## npm run dev //

3. Install dependencies from requirments.txt
! pip install -r requirements.txt

set Flask Variables for the first time
! set FLASK_APP = app.py
! set FLAST_ENV = development

to run the backend server
! flask run --reload // run under flask

to start frontend first create local server
! python -m http.server 8080

then open index file in browser