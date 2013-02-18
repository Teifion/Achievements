import transaction

from .config import config
from .achievement_models import (
    AchievementCategory,
    AchievementType,
)

def register_category(name, parent=-1, private=False, insert=True):
    if type(parent) == str:
        pass
    elif type(parent) == AchievementCategory:
        parent = parent.id
    
    a         = AchievementCategory()
    a.name    = name
    a.parent  = parent
    a.private = private
    
    a_id = None
    if insert:
        with transaction.manager:
            config['DBSession'].add(a)
            config['DBSession'].flush()
            a_id = a.id
        # config['DBSession'].expunge(a)
    
    return a_id

def register_category_tree(categories, parent=-1):
    """
    Designed for mass insertion, it takes a nested list as the categories argument and runs through it.
    If the current item is a string it takes that to be a category, if it's a list then it's a recursive
    call based on the previous item.
    
    Any item prefixed by an underscore is considered to be a private category (non-searchable)
    
    Example input:
    
    ["Top Category", [
        "Sub Cat 1",
        "Sub Cat 2", [
            "Sub Cat 2, Part 1",
            "_Sub Cat 2, Part 2",
            "_Sub Cat 2, Part 3"],
        "_Sub Cat 3",
    ]
    
    """
    
    last_item = parent
    for c in categories:
        if type(c) == str:
            if c[0] == "_":
                last_item = register_category(c[1:], parent, private=True)
            else:
                last_item = register_category(c, parent)
        else:
            register_category_tree(c, last_item)

def register_type():
    pass
