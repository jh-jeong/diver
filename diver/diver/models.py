from django.db import models


def lookup_code(mapping):
    def lookup(name):
        for c,s in mapping:
            if type(s) is tuple:
                for k,v in s:
                    if v.lower() == name.lower(): return k
            else:
                if s.lower() == name.lower(): return s
    return lookup

class Customer(models.Model):
    # Basic authentication information
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=128)
    user_id = models.ForeignKey('auth.User')

    # Body dimensions
    height_cm = models.IntegerField()
    weight_kg = models.IntegerField()
    chest_size_cm = models.IntegerField()
    waist_size_cm = models.IntegerField()
    sleeve_length_cm = models.IntegerField()
    leg_length_cm = models.IntegerField()
    BODY_SHAPES = (
        ('O', 'Abdominal obese'),
        ('M', 'Muscular'),
        ('A', 'Skinny'),
        ('B', 'Fat'),
        ('N', 'Normal'),
    )
    body_shape = models.CharField(max_length=1, choices=BODY_SHAPES)
    get_body_shape_code = lookup_code(BODY_SHAPES)

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
        )),
        ("Outer", (
        )),
        ("Bottom", (
            ('DENIM', "Denim"),
            ('SLACKS', "Slacks"),
            ('JOGGER', "Jogger"),
        )),
    )
    category = models.CharField(max_length=10, choices=CATEGORIES)
    get_category_code = lookup_code(CATEGORIES)
    @staticmethod
    def get_category1(category):
        for category1 in Item.CATEGORIES:
            for category2 in category1[1]:
                if category.upper() == category2[0].upper():
                    return category1[0]
    def category1(self):
        return Item.get_category1(self.category)

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
        ('DN', "Denim"),
    )
    material = models.CharField(max_length=2, choices=MATERIALS)
    get_material_code = lookup_code(MATERIALS)

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
        ('VS', 'Vertical'),
    )
    pattern = models.CharField(max_length=2, choices=PATTERNS)
    get_pattern_code = lookup_code(PATTERNS)

    TYPES = (
        (0, "TOP"),
        (1, "OUTER"),
        (2, "BOTTOM"),
        (3, "SHOES"),
    )
    type = models.IntegerField(choices=TYPES)

    size = models.IntegerField(null=True)
    price = models.IntegerField()
    images = models.URLField()
    comment = models.TextField()
    purchase_url = models.URLField()

    color_id1 = models.IntegerField()
    color_id2 = models.IntegerField()
    color_id3 = models.IntegerField()
    color_ratio1 = models.IntegerField()
    color_ratio2 = models.IntegerField()
    color_ratio3 = models.IntegerField()

    rate_count = models.IntegerField()

    # For Top
    sleeve_level = models.IntegerField()
    NECK_TYPES = (
        ('RN', "Round"),
        ('HR', "Henry"),
        ('HT', "Hat"),
        ('VN', "V-Neck"),
        ('ST', "Stripe"),
        ('TT', "Turtle"),
        ('CL', "Collar"),
        ('CH', "Chinese"),
    )
    neck = models.CharField(max_length=2, choices=NECK_TYPES)
    get_neck_code = lookup_code(NECK_TYPES)
    zipper = models.IntegerField()
    button = models.IntegerField()

    # For Outer
    ## sleeve_level
    ## zipper
    length_level = models.IntegerField()
    collar = models.IntegerField()
    hat = models.IntegerField()
    button = models.IntegerField()

    # For Bottom
    ## length_level
    FIT_TYPES = (
        ('ST', "Straight"),
        ('SL', "Slim"),
        ('BG', "Baggy"),
        ('SK', "Skinny"),
        ('WD', "Wide"),
        ('TP', "Tappered"),
    )
    fit = models.CharField(max_length=2, choices=FIT_TYPES)
    get_fit_code = lookup_code(FIT_TYPES)

    # For Shoes
    weight_g = models.IntegerField()
    insoles = models.IntegerField()
    brand = models.CharField(max_length=100)

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
