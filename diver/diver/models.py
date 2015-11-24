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
            ('CARDIGAN', "Cardigan"),
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
        ('NL', "Nylon"),
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
    image = models.URLField()
    rate_count = models.IntegerField()
    url = models.URLField()
    outer1 = models.ForeignKey('Item', related_name='match_for_outer1')
    outer2 = models.ForeignKey('Item', related_name='match_for_outer2')
    top1 = models.ForeignKey('Item', related_name='match_for_top1')
    top2 = models.ForeignKey('Item', related_name='match_for_top2')
    bottom = models.ForeignKey('Item', related_name='match_for_bottom')
    shoes = models.ForeignKey('Item', related_name='match_for_shoes')

class Shop(models.Model):
    name = models.CharField(max_length=30)
    url = models.URLField()
    items = models.ManyToManyField(Item)
    matches = models.ManyToManyField('Match')
    rate_count = models.IntegerField()

class Rating(models.Model):
    customer = models.ForeignKey('Customer')
    match = models.ForeignKey('Match', null=True)
    item = models.ForeignKey('Item', null=True)
    rating = models.IntegerField()

class Pref(models.Model):
    customer = models.ForeignKey(Customer)
    top_0 = models.FloatField(default=0)
    top_1 = models.FloatField(default=0)
    top_2 = models.FloatField(default=0)
    top_3 = models.FloatField(default=0)
    top_4 = models.FloatField(default=0)
    top_5 = models.FloatField(default=0)
    top_6 = models.FloatField(default=0)
    top_7 = models.FloatField(default=0)
    top_8 = models.FloatField(default=0)
    top_9 = models.FloatField(default=0)
    top_10 = models.FloatField(default=0)
    top_11 = models.FloatField(default=0)
    top_12 = models.FloatField(default=0)
    top_13 = models.FloatField(default=0)
    top_14 = models.FloatField(default=0)
    top_15 = models.FloatField(default=0)
    top_16 = models.FloatField(default=0)
    top_17 = models.FloatField(default=0)
    pattern_0 = models.IntegerField(default=0)
    pattern_1 = models.IntegerField(default=0)
    pattern_2 = models.IntegerField(default=0)
    pattern_3 = models.IntegerField(default=0)
    pattern_4 = models.IntegerField(default=0)
    pattern_5 = models.IntegerField(default=0)
    pattern_6 = models.IntegerField(default=0)
    pattern_7 = models.IntegerField(default=0)
    pattern_8 = models.IntegerField(default=0)
    pattern_9 = models.IntegerField(default=0)
    pattern_10 = models.IntegerField(default=0)
    neck_0 = models.IntegerField(default=0)
    neck_1 = models.IntegerField(default=0)
    neck_2 = models.IntegerField(default=0)
    neck_3 = models.IntegerField(default=0)
    neck_4 = models.IntegerField(default=0)
    neck_5 = models.IntegerField(default=0)
    neck_6 = models.IntegerField(default=0)
    neck_7 = models.IntegerField(default=0)
    sleeveT_0 = models.IntegerField(default=0)
    sleeveT_1 = models.IntegerField(default=0)
    sleeveT_2 = models.IntegerField(default=0)
    sleeveT_3 = models.IntegerField(default=0)
    sleeveT_4 = models.IntegerField(default=0)
    zipperO_0 = models.IntegerField(default=0)
    zipperO_1 = models.IntegerField(default=0)
    hatO_0 = models.IntegerField(default=0)
    hatO_1 = models.IntegerField(default=0)
    outer_len_0 = models.IntegerField(default=0)
    outer_len_1 = models.IntegerField(default=0)
    outer_len_2 = models.IntegerField(default=0)
    outer_len_3 = models.IntegerField(default=0)
    outer_len_4 = models.IntegerField(default=0)
    outer_button_0 = models.IntegerField(default=0)
    outer_button_1 = models.IntegerField(default=0)
    outer_button_2 = models.IntegerField(default=0)
    outer_button_3 = models.IntegerField(default=0)
    outer_button_4 = models.IntegerField(default=0)
    outer_button_5 = models.IntegerField(default=0)
    fit_0 = models.IntegerField(default=0)
    fit_1 = models.IntegerField(default=0)
    fit_2 = models.IntegerField(default=0)
    fit_3 = models.IntegerField(default=0)
    fit_4 = models.IntegerField(default=0)
    fit_5 = models.IntegerField(default=0)
    bottom_0 = models.FloatField(default=0)
    bottom_1 = models.FloatField(default=0)
    bottom_2 = models.FloatField(default=0)
    bottom_3 = models.FloatField(default=0)
    bottom_4 = models.FloatField(default=0)
    bottom_5 = models.FloatField(default=0)
    bottom_6 = models.FloatField(default=0)
    bottom_7 = models.FloatField(default=0)
    bottom_8 = models.FloatField(default=0)
    bottom_9 = models.FloatField(default=0)
    bottom_10 = models.FloatField(default=0)
    bottom_11 = models.FloatField(default=0)
    bottom_12 = models.FloatField(default=0)
    bottom_13 = models.FloatField(default=0)
    bottom_14 = models.FloatField(default=0)
    bottom_15 = models.FloatField(default=0)
    bottom_16 = models.FloatField(default=0)
    bottom_17 = models.FloatField(default=0)
