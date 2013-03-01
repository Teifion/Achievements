from pyramid.view import view_config

from .. import achievement_functions
from ..config import config

from ..achievement_models import (
    AchievementSection,
    AchievementCategory,
    AchievementSubCategory,
    AchievementType,
    Achievement,
    AchievementShowcase,
)

@view_config(route_name='achievements.ajax.list_categories', renderer='../templates/ajax/list_categories.pt', permission='achievements_admin')
def list_categories(request):
    section_id = int(request.params['section'])
    
    categories = config['DBSession'].query(AchievementCategory).filter(
        AchievementCategory.section == section_id
    ).order_by(AchievementCategory.name.asc())
    
    request.do_not_log = True
    return dict(
        section_id = section_id,
        categories = list(categories)
    )

@view_config(route_name='achievements.ajax.list_subcategories', renderer='../templates/ajax/list_subcategories.pt', permission='achievements_admin')
def list_subcategories(request):
    category_id = int(request.params['category'])
    
    subcategories = config['DBSession'].query(AchievementSubCategory).filter(
        AchievementSubCategory.category == category_id
    ).order_by(AchievementSubCategory.name.asc())
    
    request.do_not_log = True
    return dict(
        subcategories = list(subcategories),
        category_id = category_id,
    )

@view_config(route_name='achievements.ajax.list_achievements', renderer='../templates/ajax/list_achievements.pt', permission='achievements_admin')
def list_achievements(request):
    subcategory_id = int(request.params['subcategory'])
    
    achievements = config['DBSession'].query(AchievementType).filter(
        AchievementType.subcategory == subcategory_id
    ).order_by(AchievementType.name.asc())
    
    request.do_not_log = True
    return dict(
        achievements = list(achievements),
        subcategory_id = subcategory_id,
    )
