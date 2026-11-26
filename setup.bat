@echo off
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
echo.
echo Done. Start the site with:  python manage.py runserver
echo Demo login: demo / ChemDemo@2026
pause
