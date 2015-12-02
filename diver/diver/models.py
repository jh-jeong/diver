from django.db import models


def lookup_code(mapping):
    def lookup(name):
        for c,s in mapping:
            if type(s) is tuple:
                for k,v in s:
                    if v.strip().lower() == name.strip().lower(): return k
            else:
                if s.strip().lower() == name.strip().lower(): return c
    return lookup

class ItemPref(models.Model):
    customer = models.ForeignKey('Customer', null=True)
    item = models.ForeignKey('Item', null=True)
    score = models.IntegerField()

class Customer(models.Model):
    # Basic authentication information
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=128)
    user = models.ForeignKey('auth.User')

    # Body dimensions
    height_cm = models.IntegerField()
    weight_kg = models.IntegerField()
    chest_size_cm = models.IntegerField()
    waist_size_cm = models.IntegerField()
    sleeve_length_cm = models.IntegerField()
    leg_length_cm = models.IntegerField()
    shoes_size_mm = models.IntegerField()
    BODY_SHAPES = (
        ('O', 'Abdominal obese'),
        ('M', 'Muscular'),
        ('A', 'Skinny'),
        ('B', 'Fat'),
        ('N', 'Normal'),
    )
    body_shape = models.CharField(max_length=1, choices=BODY_SHAPES)
    get_body_shape_code = lookup_code(BODY_SHAPES)

    def like(item, score):
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

    # List of types.
    TYPES = (
        (0, "TOP"),
        (1, "OUTER"),
        (2, "BOTTOM"),
        (3, "SHOES"),
    )
    type = models.IntegerField(choices=TYPES)
    get_type_code = lookup_code(TYPES)

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
        ('MC', 'MultiCOLors'),
        ('NO', 'None'),
        ('PR', 'Printed'),
        ('SF', 'Snowflake'),
        ('ST', 'Striped'),
        ('TW', 'Twisted'),
        ('VS', 'Vertical'),
    )
    pattern = models.CharField(max_length=2, choices=PATTERNS)
    get_pattern_code = lookup_code(PATTERNS)


    price = models.IntegerField()
    images = models.URLField()
    comment = models.TextField()
    purchase_url = models.URLField()

    rate_count = models.IntegerField(default=0)

    # For Top
    sleeve_level = models.IntegerField(null=True)
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
    # button = models.IntegerField(null=True)
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
    jean_washing = models.IntegerField(null=True)

    # For Shoes
    weight_g = models.IntegerField(null=True)
    insoles = models.IntegerField(null=True)
    brand = models.CharField(max_length=100, null=True)

    #shop = models.ForeignKey(through = 'Shop')

class Color(models.Model):
    item = models.ForeignKey('Item')
    COLOR_VALUES = (
        (0, (0xF5, 0xF5, 0xDC)),
        (1, (0x00, 0x00, 0x00)),
        (2, (0x00, 0x00, 0xFF)),
        (3, (0xA5, 0x2A, 0x2A)),
        (4, (0xFF, 0xD7, 0x00)),
        (5, (0x00, 0x80, 0x00)),
        (6, (0x80, 0x80, 0x80)),
        (7, (0xF0, 0xF6, 0x8C)),
        (8, (0xF5, 0xFF, 0xFA)),
        (9, (0x00, 0x00, 0x80)),
        (10,(0xFF, 0xA5, 0x00)),
        (11,(0xFF, 0xC0, 0xCB)),
        (12,(0xFF, 0x00, 0x00)),
        (13,(0x87, 0xCE, 0xEB)),
        (14,(0xFF, 0xFF, 0xFF)),
        (15,(0xFF, 0xFF, 0x00)),
        (16,(0xA9, 0xA9, 0xA9)),
        (17,(0xFF, 0xFF, 0xF0)),
        (18,(0x80, 0x00, 0x80)),
        (19,(0x00, 0x64, 0x00)),
    )
    COLORS = (
        (0, "Beige"),
        (1, "Black"),
        (2, "Blue"),
        (3, "Brown"),
        (4, "Gold"),
        (5, "Green"),
        (6, "Grey"),
        (7, "Khaki"),
        (8, "Mint"),
        (9, "Navy"),
        (10, "Orange"),
        (11, "Pink"),
        (12, "Red"),
        (13, "Skyblue"),
        (14, "White"),
        (15, "Yellow"),
        (16, "Charcoal"),
        (17, "Ivory"),
        (18, "Purple"),
        (19, "Dark green"),
    )
    get_color_code = lookup_code(COLORS)
    color_id1 = models.SmallIntegerField(choices=COLORS)
    color_id2 = models.SmallIntegerField(choices=COLORS, null=True)
    color_id3 = models.SmallIntegerField(choices=COLORS, null=True)
    color_ratio1 = models.SmallIntegerField()
    color_ratio2 = models.SmallIntegerField()
    color_ratio3 = models.SmallIntegerField()

class Size(models.Model):
    item = models.ForeignKey('Item')

    # For Top
    length_cm = models.IntegerField(null=True)
    shoulder_cm = models.IntegerField(null=True)
    chest_cm = models.IntegerField(null=True)
    sleeve_cm = models.IntegerField(null=True)
    letter = models.CharField(max_length=5, null=True)

    # For Outer
    ## Shares attributes with Top

    # For Bottom
    ## length_cm
    waist_cm = models.IntegerField(null=True)
    thigh_cm = models.IntegerField(null=True)
    crotch_cm = models.IntegerField(null=True)
    ## letter

    # For Shoes
    size_mm = models.IntegerField(null=True)
    correction = models.IntegerField(null=True)

class Match(models.Model):
    image = models.URLField()
    rate_count = models.IntegerField(default=0)
    url = models.URLField()
    outer1 = models.ForeignKey('Color', related_name='match_for_outer1', null=True)
    outer2 = models.ForeignKey('Color', related_name='match_for_outer2', null=True)
    top1 = models.ForeignKey('Color', related_name='match_for_top1', null=True)
    top2 = models.ForeignKey('Color', related_name='match_for_top2', null=True)
    bottom = models.ForeignKey('Color', related_name='match_for_bottom', null=True)
    shoes = models.ForeignKey('Color', related_name='match_for_shoes', null=True)

class Shop(models.Model):
    name = models.CharField(max_length=30)
    url = models.URLField()
    items = models.ManyToManyField(Item)
    matches = models.ManyToManyField('Match')
    rate_count = models.IntegerField()

class Rating(models.Model):
    customer = models.ForeignKey('Customer')
    match = models.ForeignKey('Match', null=True)

    def score_range_validator(score):
        if not (-2 <= score <= 2):
            raise ValidationError("Rating should be between -2 and 2, inclusively.")
    score = models.SmallIntegerField(default=0, validators=[score_range_validator])

class Pref(models.Model):
    customer = models.ForeignKey(Customer)
    pattern_CM = models.IntegerField(default=0)
    pattern_CH = models.IntegerField(default=0)
    pattern_FL = models.IntegerField(default=0)
    pattern_GR = models.IntegerField(default=0)
    pattern_LG = models.IntegerField(default=0)
    pattern_MC = models.IntegerField(default=0)
    pattern_NO = models.IntegerField(default=0)
    pattern_PR = models.IntegerField(default=0)
    pattern_SF = models.IntegerField(default=0)
    pattern_ST = models.IntegerField(default=0)
    pattern_VS = models.IntegerField(default=0)
    neck_RN = models.IntegerField(default=0)
    neck_HR = models.IntegerField(default=0)
    neck_HT = models.IntegerField(default=0)
    neck_VN = models.IntegerField(default=0)
    neck_ST = models.IntegerField(default=0)
    neck_TT = models.IntegerField(default=0)
    neck_CL = models.IntegerField(default=0)
    neck_CH = models.IntegerField(default=0)
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
    fit_ST = models.IntegerField(default=0)
    fit_SL = models.IntegerField(default=0)
    fit_BG = models.IntegerField(default=0)
    fit_SK = models.IntegerField(default=0)
    fit_WD = models.IntegerField(default=0)
    fit_TP = models.IntegerField(default=0)
