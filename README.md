# Project DIVER
Indivisualized fashion recommendation shopping system

### Installation
```
(make virtualenv directory under name 'venv')
source venv/bin/activate
pip install -r requirements.txt
```

### Memcached installation and deployment
Ubuntu:
```
sudo apt-get install memcached
memcached -d -p 20404
```

### Initial data installation
```
diver/manage.py migrate
diver/manage.py loaddata diver/data.json
```

### Run test server
```
diver/manage.py runserver 0.0.0.0:8080
```
