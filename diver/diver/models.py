from django.db import models


class Customer(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=128)
    height_cm = models.IntegerField()
    weight_km = models.IntegerField()
    shirt_size = models.IntegerField()
    pants_size = models.IntegerField()
    cap_size = models.IntegerField()
    # body shape

    def like(item):
        pass

    def dislike(item):
        pass

    def modify_score(recommendation):
        pass


class Image(models.Model):
    filename = models.CharField(max_length=30)
    image = models.ImageField(null=True)

class Item(models.Model):
    name = models.CharField(max_length=30)

    # List of categories.
    # Category code should not be longer than 10 chars.
    CATEGORIES = (
        ("Top", (
            ('SHIRT', "Shirt"),
            ('TSHIRT', "T-shirt"),
            ('SLEEVELESS', "Sleeveless"),
            ('KNIT', "Knit"),
            ('HOOD', "Hood"),
            ('CREW', "Crew sweatshirt"),
        ),
    )
    category = models.CharField(max_length=10, choices=CATEGORIES)

    # List of materials.
    # Material code should be 2 chars.
    MATERIALS = (
        ('AC', "Acrylic"),
        ('CD', "Corduroy"), 
        ('CT', "Cotton"),
        ('LN', "Linen"),
        ('NP', "Neoprene"),
        ('OX', "Oxford"),
        ('PG', "Pigment"),
        ('PL', "Poly"),
        ('SL', "Slub"),
        ('TW', "Tweed"),
        ('WL', "Wool"),
    )
    material = models.CharField(max_length=2, choices=MATERIALS)

    # List of patterns.
    # Pattern code should be 2 chars.
    PATTERNS = (
        ('CM', 'Camoflage'),
        ('CH', 'Checked'),
        ('FL', 'Floral'),
        ('GR', 'Gradation'),
        ('LG', 'Logo'),
        ('MC', 'Multicolors'),
        ('NO', 'None'), 
        ('PR', 'Printed'), 
        ('SF', 'Snowflake'),
        ('ST', 'Striped'),
        ('TW', 'Twisted'),
    )
    pattern = models.CharField(max_length=2, choices=PATTERNS)

    sleeve_length = models.IntegerField()
    size = models.IntegerField()
    price = models.IntegerField()
    images = models.ManyToManyField(Image)
    purchase_url = models.URLField()
    #shop = models.ForeignKey(through = 'Shop')


class Match(models.Model):
    items = models.ManyToManyField(Item)
    images = models.ManyToManyField(Image)

class Shop(models.Model):
    name = models.CharField(max_length=30)
    url = models.URLField()
    items = models.ManyToManyField(Item)
    matches = models.ManyToManyField(Match)

class Like(models.Model):
    customer_id = models.ImageField(null=False)
    item_id = models.IntegerField(null=False)
