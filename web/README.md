# Setup
Create venv in web folder and install the additional dependencies found in `setup/requirements.txt`.

Adjust the path in `highscores_uwsgi.ini`. Now start the uwsgi server:
```sh
uwsgi --ini highscores_uwsgi.ini
```
Monitor the log file for unusual things.

Add proxy pass to Nginx:
```nginx
location /mastermind { try_files $uri @mastermind; }
location @mastermind {
    include uwsgi_params;
    uwsgi_pass unix:/FULL_PATH_TO_SOCKET_FILE;
}  
```


