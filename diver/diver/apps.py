import os, sys
sys.path.append(os.path.abspath('../algo'))
sys.path.append(os.path.abspath('..'))

from django.apps import AppConfig
from django.db import connection

import category
import size
import color
import item

class DiverConfig(AppConfig):
    name = 'diver'
    verbose_name = 'Diver'

    def ready(self):
        # Startup code here
        try:
            category.init_category(connection.cursor())
            size.init_size(connection.cursor())
            color.init_color(connection.cursor())
            item.init_rating(connection.cursor())
        except:
            print("Algorithm initialization failed.")
