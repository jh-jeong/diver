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
cd diver
./manage.py migrate
./manage.py loaddata data.json
```

### Run test server
```
cd diver
./manage.py runserver 0.0.0.0:8080
```
