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
            ('STJP', "Stadium jumper"),
            ('BLOUSON', "Blouson"),
            ('JUMPER', "Jumper"),
            ('JACKET', "Jacket"),
            ('COAT', "Coat"),
            ('VEST', "Vest"),
            ('DENIM', "Denim"),
        )),
        ("Bottom", (
            ('JEAN', "Jean"),
            ('COTTON', "Cotton"),
            ('SLACKS', "Slacks"),
            ('JOGGER', "Jogger"),
            ('BAGGY', "Baggy"),
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
        ('LT', "Leather"),
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
    get_type_code = lookup_code(TYPES)

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

    rate_count = models.IntegerField(default=0)

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
    neck = models.CharField(max_length=2, choices=NECK_TYPES, null=True)
    get_neck_code = lookup_code(NECK_TYPES)
    zipper = models.IntegerField(null=True)
    button = models.IntegerField(null=True)

    # For Outer
    ## sleeve_level
    ## zipper
    length_level = models.IntegerField(null=True)
    collar = models.IntegerField(null=True)
    hat = models.IntegerField(null=True)
    button = models.IntegerField(null=True)
    padding = models.IntegerField(null=True)

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
    fit = models.CharField(max_length=2, choices=FIT_TYPES, null=True)
    get_fit_code = lookup_code(FIT_TYPES)

    # For Shoes
    weight_g = models.IntegerField(null=True)
    insoles = models.IntegerField(null=True)
    brand = models.CharField(max_length=100, null=True)

    #shop = models.ForeignKey(through = 'Shop')

class Size(models.Model):
    item = models.ForeignKey('Item')

    # For Top
    length_cm = models.IntegerField()
    shoulder_cm = models.IntegerField()
    chest_cm = models.IntegerField()
    sleeve_cm = models.IntegerField()
    letter = models.CharField(max_length=5)

    # For Outer
    ## Shares attributes with Top

    # For Bottom
    ## length_cm
    waist_cm = models.IntegerField()
    thigh_cm = models.IntegerField()
    crotch_cm = models.IntegerField()
    ## letter

    # For Shoes
    size_mm = models.IntegerField()
    correction = models.IntegerField()

class Match(models.Model):
    items = models.ManyToManyField(Item)
    images = models.ManyToManyField(Image)

class Shop(models.Model):
    name = models.CharField(max_length=30)
    url = models.URLField()
    items = models.ManyToManyField(Item)
    matches = models.ManyToManyField(Match)
    rate_count = models.IntegerField()

class Like(models.Model):
    customer_id = models.ImageField(null=False)
    item_id = models.IntegerField(null=False)
