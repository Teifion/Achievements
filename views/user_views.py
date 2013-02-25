from pyramid.view import (
    view_config,
)

from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import get_renderer

from .. import achievement_functions
from ..config import config

from ..achievement_models import (
    AchievementType,
    Achievement,
    AchievementShowcase,
)

@view_config(route_name='achievements.dashboard', renderer='../templates/home.pt', permission='achievements')
@view_config(route_name='achievements.user', renderer='../templates/home.pt', permission='achievements')
def achievement_dashboard(request):
    layout = get_renderer(config['layout']).implementation()
    
    if 'user_id' in request.matchdict:
        user_id = int(request.matchdict['user_id'])
        player_name = config['DBSession'].query(config['User'].name).filter(config['User'].id == user_id).one()[0]
    else:
        user_id = request.user.id
        player_name = request.user.name
        
    # Showcase chosen by user
    showcase = config['DBSession'].query(AchievementShowcase.items).filter(AchievementShowcase.user == user_id).first()
    if showcase == None:
        showcase = AchievementShowcase()
        showcase.items = [0]*5
    
    completed = []
    pending = []
    recents = []
    type_ids = set(showcase.items)
    for a in config['DBSession'].query(Achievement).filter(Achievement.user == user_id).order_by(Achievement.first_awarded.desc()):
        if a.first_awarded == None:
            pending.append(a)
        else:
            if len(recents) < 5:
                recents.append(a)
            completed.append(a)
        
        type_ids.add(a.item)
    
    achievement_types = {}
    for a in config['DBSession'].query(AchievementType).filter(AchievementType.id.in_(type_ids)):
        achievement_types[a.id] = a
    
    return dict(
        title  = "Achievements for {}".format(player_name),
        layout = layout,
        pending = pending,
        completed = completed,
        achievement_types = achievement_types,
        recents = recents,
        showcase = showcase,
        sections = achievement_functions.sections,
        user_id = user_id,
        player_name = player_name,
    )

@view_config(route_name='achievements.search', renderer='../templates/search.pt', permission='achievements')
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

@view_config(route_name='achievements.category', renderer='../templates/category.pt', permission='achievements')
def achievements_category(request):
    layout = get_renderer(config['layout']).implementation()
    
    user_id      = int(request.matchdict['user_id'])
    category = request.matchdict['category']
    
    return dict(
        title  = "%s achievements" % category,
        layout = layout,
        category = achievement_functions.sections[category],
        user_id = user_id,
        sub_categories = achievement_functions.sections[category]['sub_categories'],
    )

@view_config(route_name='achievements.sub_category', renderer='../templates/sub_category.pt', permission='achievements')
def achievements_sub_category(request):
    layout = get_renderer(config['layout']).implementation()
    
    user_id      = int(request.matchdict['user_id'])
    category     = request.matchdict['category']
    sub_category = request.matchdict['sub_category']
    
    # I wanted to use something like this but I couldn't get the outer-join to work correctly :(
    # achievement_list = config['DBSession'].query(AchievementType, Achievement).outerjoin(
    #     Achievement, Achievement.item == AchievementType.id
    # ).filter(
    #     AchievementType.lookup.in_(achievement_names),
    #     Achievement.user == request.user.id,
    # )
    
    achievement_names = achievement_functions.sections[category]['sub_categories'][sub_category]['achievements']
    
    achievement_types = {}
    lookup = {}
    for a in config['DBSession'].query(AchievementType).filter(AchievementType.lookup.in_(achievement_names)):
        achievement_types[a.id] = a
        lookup[a.lookup] = a.id
    
    player_achievements = {}
    for a in config['DBSession'].query(Achievement).filter(Achievement.item.in_(achievement_types), Achievement.user == user_id):
        player_achievements[a.item] = a
    
    complete, partial, not_started = [], [], []
    for a in [lookup[a] for a in achievement_names]:
        if a in player_achievements:
            if player_achievements[a].activation_count >= achievement_types[a].activation_count:
                complete.append(a)
            else:
                partial.append(a)
        else:
            not_started.append(a)
    
    return dict(
        title  = "%s achievements" % achievement_functions.sections[category]['sub_categories'][sub_category]['name'],
        layout = layout,
        category = achievement_functions.sections[category],
        sub_category = achievement_functions.sections[category]['sub_categories'][sub_category],
        user_id = user_id,
        achievement_list = complete + partial + not_started,
        achievement_types = achievement_types,
        player_achievements = player_achievements,
    )

@view_config(route_name='achievements.showcase_popup', renderer='../templates/showcase_popup.pt', permission='achievements')
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
