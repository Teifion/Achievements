import datetime
from .achievement_models import (
    AchievementSection,
    AchievementCategory,
    AchievementSubCategory,
    AchievementType,
    Achievement,
)
import transaction
from .config import config

def editors_for_achievement(the_achievement_type):
    editors = config['DBSession'].query(AchievementSection.editors).filter(
        AchievementSubCategory.id == the_achievement_type.subcategory,
        AchievementCategory.id == AchievementSubCategory.category,
        AchievementSection.id == AchievementCategory.section
    ).first()
    
    if editors == None:
        return []
    return editors[0]

def editors_for_subcategory(the_subcategory):
    editors = config['DBSession'].query(AchievementSection.editors).filter(
        AchievementCategory.id == the_subcategory.category,
        AchievementSection.id == AchievementCategory.section
    ).first()
    
    if editors == None:
        return []
    return editors[0]

def editors_for_category(the_category):
    editors = config['DBSession'].query(AchievementSection.editors).filter(
        AchievementSection.id == the_category.section
    ).first()
    
    if editors == None:
        return []
    return editors[0]

def register(achievement_list):
    """Takes a list of achievement type (or dict) and ensures they exist
    within the database. Any type not in the database is added."""
    
    # If it's a dictionary convert it into an AchievementType
    achievement_list = [AchievementType(*a) if type(a) == tuple else a for a in achievement_list]
    
    # Who are we missing?
    names = [a.lookup for a in achievement_list]
    found = []
    for n in config['DBSession'].query(AchievementType.lookup).filter(AchievementType.lookup.in_(names)):
        found.append(n[0])
    
    with transaction.manager:
        for a in achievement_list:
            if a.lookup not in found:
                config['DBSession'].add(a)

def get_achievements(filters, user_id=-1, limit=20, order_by=[], achieved=True):
    filters = list(filters)
    filters.append(Achievement.item == AchievementType.id)
    
    if achieved:
        filters.extend([
            Achievement.activation_count >= AchievementType.activation_count,
        ])
    
    if type(user_id) == int:
        filters.extend([
            Achievement.user == user_id,
        ])
    elif type(user_id) in (list, tuple):
        filters.extend([
            Achievement.user.in_(user_id),
        ])
    else:
        if user_id != None:
            raise Exception("No handler for user_id of type %s" % type(user_id))
    
    return config['DBSession'].query(Achievement, AchievementType).filter(*filters).order_by(*order_by).limit(limit)

def give_achievement(achievement_lookup, user_id, acount=1):
    the_item = config['DBSession'].query(AchievementType).filter(AchievementType.lookup == achievement_lookup).limit(1).first()
    
    if the_item == None:
        raise KeyError("No item by lookup of '{}'".format(achievement_lookup))
    
    the_achievement = config['DBSession'].query(Achievement).filter(
        Achievement.item == the_item.id, Achievement.user == user_id).limit(1).first()
    
    if the_achievement == None:
        the_achievement                  = Achievement()
        the_achievement.user             = user_id
        the_achievement.item             = the_item.id
        the_achievement.activation_count = 0
        the_achievement.awarded    = None
    
    # No reason to stop counting just because we've achievemed the thing once
    origional_count = the_achievement.activation_count
    the_achievement.activation_count += acount
    
    # It's been awarded, we need to see if they "achieve" it again and thus refresh the expiration date
    if the_achievement.awarded != None:
        amount_over_target = origional_count % the_item.activation_count
        
        # Take the amount we were over the actviation target and add the new extra
        # if it takes us back over the target we re-issue the achievement
        amount_over_target += acount
        
        if amount_over_target >= the_item.activation_count:
            the_achievement.last_awarded = datetime.datetime.now()
            
            if the_item.duration != None:
                the_achievement.expires = the_achievement.last_awarded + the_item.duration
    
    # Not awarded yet, now we award it
    if the_achievement.activation_count >= the_item.activation_count and the_achievement.awarded == None:
        the_achievement.awarded = datetime.datetime.now()
        
        if the_item.duration != None:
            the_achievement.expires = the_achievement.last_awarded + the_item.duration
    
    config['DBSession'].add(the_achievement)
