from ...models import (
    DBSession,
)

import datetime
from .achievement_models import AchievementType, Achievement
import transaction

def register(achievement_list):
    """Takes a list of achievement type (or dict) and ensures they exist
    within the database. Any type not in the database is added."""
    
    # If it's a dictionary convert it into an AchievementType
    achievement_list = [AchievementType(*a) if type(a) == tuple else a for a in achievement_list]
    
    # Who are we missing?
    names = [a.name for a in achievement_list]
    found = []
    for n in DBSession.query(AchievementType.name).filter(AchievementType.name.in_(names)):
        found.append(n[0])
    
    with transaction.manager:
        for a in achievement_list:
            if a.name not in found:
                DBSession.add(a)

def give_achievement(achievement_lookup, user_id, acount=1):
    the_item = DBSession.query(AchievementType).filter(AchievementType.lookup == achievement_lookup).limit(1).first()
    
    if the_item == None:
        raise KeyError("No item by lookup of '{}'".format(achievement_lookup))
    
    the_achievement = DBSession.query(Achievement).filter(
        Achievement.item == the_item.id, Achievement.user == user_id).limit(1).first()
    
    if the_achievement == None:
        the_achievement                  = Achievement()
        the_achievement.user             = user_id
        the_achievement.item             = the_item.id
        the_achievement.activation_count = 0
        the_achievement.first_awarded    = None
        the_achievement.last_awarded     = None
    
    # No reason to stop counting just because we've achievemed the thing once
    origional_count = the_achievement.activation_count
    the_achievement.activation_count += acount
    
    # It's been awarded, we need to see if they "achieve" it again and thus refresh the expiration date
    if the_achievement.first_awarded != None:
        amount_over_target = origional_count % the_item.activation_count
        
        # Take the amount we were over the actviation target and add the new extra
        # if it takes us back over the target we re-issue the achievement
        amount_over_target += acount
        
        if amount_over_target >= the_item.activation_count:
            the_achievement.last_awarded = datetime.datetime.now()
            
            if the_item.duration != None:
                the_achievement.expires = the_achievement.last_awarded + the_item.duration
    
    # Not awarded yet, now we award it
    if the_achievement.activation_count >= the_item.activation_count and the_achievement.first_awarded == None:
        the_achievement.first_awarded = datetime.datetime.now()
        the_achievement.last_awarded = datetime.datetime.now()
        
        if the_item.duration != None:
            the_achievement.expires = the_achievement.last_awarded + the_item.duration
    
    DBSession.add(the_achievement)
