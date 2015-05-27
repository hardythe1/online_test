import subprocess
import os
os.system("django-admin.py startproject my_demo")
settings_path = os.getcwd()+"/my_demo/my_demo/settings.py"
os.system("wget -Nq https://raw.githubusercontent.com/hardythe1/online_test/remotes/origin/RemoveBuildout/online_test/settings.py -O "+settings_path)
os.system("wget -Nq https://raw.githubusercontent.com/hardythe1/online_test/remotes/origin/RemoveBuildout/online_test/urls.py -O "+settings_path)
os.chdir(os.getcwd()+"/my_demo/")
os.system("python manage.py syncdb --noinput")
os.system("python manage.py loaddata initial_fixtures.json")
os.system("python manage.py runserver")
