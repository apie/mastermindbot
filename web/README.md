# Web setup
Create venv in web folder and install the additional dependencies found in `web/setup/requirements.txt`:
```sh
cd web
virtualenv -p python3 venv
source venv/bin/activate
pip install -r setup/requirements.txt
```

Now start the gunicorn server:
```sh
gunicorn highscores:app
```

Add proxy pass to Nginx `server` block:
```nginx
location /mastermind { try_files $uri @mastermind; }
location @mastermind {
  include proxy_params;
  proxy_pass http://localhost:8000;
}
```


