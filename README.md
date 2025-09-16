"# medical-billing-system" 

for this command for run the project 
  1- create venv 
  # Windows
  python -m venv venv

  2-active 
  venv\Scripts\activate
  
  # Linux/MacOS
  python3 -m venv venv
  source venv/bin/activate

  python manage.py migrate
  python manage.py createsuperuser
  python manage.py runserver     (http://localhost:8000)
