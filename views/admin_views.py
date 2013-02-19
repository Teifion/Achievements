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

@view_config(route_name='achievements.admin', renderer='../templates/admin/home.pt', permission='achievements_admin')
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
