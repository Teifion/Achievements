from pyramid.view import (
    view_config,
)

from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import get_renderer

from sqlalchemy import and_
from .. import achievement_functions
from ..config import config

from ..achievement_models import (
    AchievementType,
    Achievement,
    AchievementSection,
    AchievementCategory,
    AchievementSubCategory,
    AchievementShowcase,
)

@view_config(route_name='achievements.dashboard', renderer='../templates/user/home.pt', permission='achievements')
@view_config(route_name='achievements.user', renderer='../templates/user/home.pt', permission='achievements')
def achievement_dashboard(request):
    layout = get_renderer(config['layout']).implementation()
    
    if 'user_id' in request.matchdict:
        attrs = (
            getattr(config['User'], config['user.id_property']),
            getattr(config['User'], config['user.name_property'])
        )
        
        user_id     = int(request.matchdict['user_id'])
        player_name = config['DBSession'].query(attrs[1]).filter(attrs[0] == user_id).one()[0]
        
    else:
        the_user    = config['get_user'](request)
        user_id     = the_user.id
        player_name = the_user.name
    
    # Showcase chosen by user
    showcase = list(config['DBSession'].query(AchievementType).filter(AchievementType.id == AchievementShowcase.achievement, AchievementShowcase.user == user_id).order_by(AchievementShowcase.placement.desc()).limit(5))
    
    while len(showcase) < 5:
        showcase.append(None)
    
    recents = config['DBSession'].query(Achievement, AchievementType).filter(Achievement.user == user_id, Achievement.item == AchievementType.id, Achievement.awarded != None).order_by(Achievement.awarded.desc()).limit(5)
    
    # The sections to list
    sections = config['DBSession'].query(AchievementSection).order_by(AchievementSection.name.asc())
    
    return dict(
        title       = "Achievements for {}".format(player_name),
        layout      = layout,
        showcase    = showcase,
        sections    = sections,
        user_id     = user_id,
        player_name = player_name,
        recents     = recents,
    )

@view_config(route_name='achievements.section', renderer='../templates/user/section.pt', permission='achievements')
def achievement_sections(request):
    layout = get_renderer(config['layout']).implementation()
    
    attrs = (
        getattr(config['User'], config['user.id_property']),
        getattr(config['User'], config['user.name_property'])
    )
    
    user_id     = int(request.matchdict['user_id'])
    player_name = config['DBSession'].query(attrs[1]).filter(attrs[0] == user_id).one()[0]
    
    section_id = int(request.matchdict['section_id'])
    the_section = config['DBSession'].query(AchievementSection).filter(AchievementSection.id == section_id).first()
    
    # The categories to list
    categories = config['DBSession'].query(AchievementCategory).filter(AchievementCategory.section == section_id).order_by(AchievementCategory.name.asc())
    
    return dict(
        title       = "Achievements for {}".format(player_name),
        layout      = layout,
        categories  = categories,
        user_id     = user_id,
        player_name = player_name,
        the_section = the_section,
    )

@view_config(route_name='achievements.category', renderer='../templates/user/category.pt', permission='achievements')
def achievement_categories(request):
    layout = get_renderer(config['layout']).implementation()
    
    attrs = (
        getattr(config['User'], config['user.id_property']),
        getattr(config['User'], config['user.name_property'])
    )
    
    user_id     = int(request.matchdict['user_id'])
    player_name = config['DBSession'].query(attrs[1]).filter(attrs[0] == user_id).one()[0]
    
    category_id = int(request.matchdict['category_id'])
    the_category = config['DBSession'].query(AchievementCategory).filter(AchievementCategory.id == category_id).first()
    
    # The categories to list
    subcategories = config['DBSession'].query(AchievementSubCategory).filter(AchievementSubCategory.category == category_id).order_by(AchievementSubCategory.name.asc())
    
    return dict(
        title         = "Achievements for {}".format(player_name),
        layout        = layout,
        subcategories = subcategories,
        the_category  = the_category,
        user_id       = user_id,
        player_name   = player_name,
    )


@view_config(route_name='achievements.sub_category', renderer='../templates/user/sub_category.pt', permission='achievements')
def achievements_sub_category(request):
    layout = get_renderer(config['layout']).implementation()
    
    attrs = (
        getattr(config['User'], config['user.id_property']),
        getattr(config['User'], config['user.name_property'])
    )
    
    user_id     = int(request.matchdict['user_id'])
    player_name = config['DBSession'].query(attrs[1]).filter(attrs[0] == user_id).one()[0]
    
    sub_category_id = int(request.matchdict['subcategory_id'])
    the_sub_category = config['DBSession'].query(AchievementSubCategory).filter(AchievementSubCategory.id == sub_category_id).first()
    
    # SELECT achievement_types.name, achievements.awarded FROM achievement_types
    #     LEFT OUTER JOIN achievements ON (achievement_types.id = achievements.item AND achievements.user = 1)
    # WHERE achievement_types.subcategory = 1
    # ORDER BY achievement_types.id ASC
    
    achievements = config['DBSession'].query(AchievementType, Achievement).outerjoin(
        Achievement, (
            and_(
                Achievement.item == AchievementType.id,
                Achievement.user == user_id,
            ))).filter(AchievementType.subcategory == sub_category_id)
    
    print(achievements)
    
    # filter(*filters)
    
    # achievement_types = {}
    # lookup = {}
    # for a in config['DBSession'].query(AchievementType).filter(AchievementType.lookup.in_(achievement_names)):
    #     achievement_types[a.id] = a
    #     lookup[a.lookup] = a.id
    
    # player_achievements = {}
    # for a in config['DBSession'].query(Achievement).filter(Achievement.item.in_(achievement_types), Achievement.user == user_id):
    #     player_achievements[a.item] = a
    
    # complete, partial, not_started = [], [], []
    # for a in [lookup[a] for a in achievement_names]:
    #     if a in player_achievements:
    #         if player_achievements[a].activation_count >= achievement_types[a].activation_count:
    #             complete.append(a)
    #         else:
    #             partial.append(a)
    #     else:
    #         not_started.append(a)
    
    return dict(
        title           = "Achievements for {}".format(player_name),
        player_name     = player_name,
        layout          = layout,
        the_sub_category = the_sub_category,
        user_id         = user_id,
        achievements    = achievements,
    )

@view_config(route_name='achievements.search', renderer='../templates/user/search.pt', permission='achievements')
def achievements_search(request):
    layout = get_renderer(config['layout']).implementation()
    message = ""
    
    if "player_name" in request.params:
        player_id = config['DBSession'].query(config['User'].id).filter(config['User'].name == request.params['player_name'].upper()).first()
        
        if player_id == None:
            message = "We cannot find anyone with the username '{}'".format(request.params['player_name'])
        else:
            player_id = player_id[0]
            
            return HTTPFound(location=request.route_url('achievements.user', user_id=player_id))
    
    return dict(
        title  = "Achievements: Player search",
        layout = layout,
        message = message,
    )

@view_config(route_name='achievements.showcase_popup', renderer='../templates/user/showcase_popup.pt', permission='achievements')
def achievements_showcase_popup(request):
    achievement_list = config['DBSession'].query(AchievementType.id, AchievementType.name
        ).filter(Achievement.last_awarded != None, Achievement.user == request.user.id, AchievementType.id == Achievement.item
        ).order_by(AchievementType.name.asc())
    
    # Get a list of all achievements
    return dict(
        achievement_list = list(achievement_list)
    )

@view_config(route_name='achievements.edit_showcase', permission='achievements')
def achievements_edit_showcase(request):
    showcase_number = int(request.params['showcase_number'])
    achievement_id = int(request.params['achievement_id'])
    
    # Showcase chosen by user
    showcase = config['DBSession'].query(AchievementShowcase).filter(AchievementShowcase.user == request.user.id).first()
    if showcase == None:
        showcase = AchievementShowcase()
        showcase.user = request.user.id
        showcase.items = [0]*5
    
    showcase.items[showcase_number] = achievement_id
    showcase.items = tuple(showcase.items)
    config['DBSession'].add(showcase)
    
    # Get a list of all achievements
    return HTTPFound(location=request.route_url('achievements.dashboard'))
