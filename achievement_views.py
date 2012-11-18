import transaction

from pyramid.view import (
    view_config,
)

from pyramid.httpexceptions import (
    HTTPFound,
)

from pyramid.renderers import get_renderer
from sqlalchemy import or_

from . import achievement_functions

from ...models import (
    DBSession,
    User,
    AchievementType,
    Achievement,
)

@view_config(route_name='achievements_dashboard', renderer='templates/achievement_dashboard.pt', permission='loggedin')
def achievement_dashboard(request):
    layout = get_renderer('../../templates/layouts/empty.pt').implementation()
    
    completed = []
    pending = []
    type_ids = set()
    for a in DBSession.query(Achievement).filter(Achievement.user == request.user.id).order_by(Achievement.first_awarded.desc()):
        if a.first_awarded == None:
            pending.append(a)
        else:
            completed.append(a)
        
        type_ids.add(a.item)
    
    achievement_types = {}
    for a in DBSession.query(AchievementType).filter(AchievementType.id.in_(type_ids)):
        achievement_types[a.id] = a
    
    return dict(
        title  = "Achievements",
        layout = layout,
        pending = pending,
        completed = completed,
        achievement_types = achievement_types,
    )

@view_config(route_name='user_achievements', renderer='templates/user_achievements.pt', permission='loggedin')
def user_achievements(request):
    layout = get_renderer('../../templates/layouts/empty.pt').implementation()
    
    return dict(
        title  = "Achievements",
        layout = layout
    )

@view_config(route_name='achievements_category', renderer='templates/achievements_category.pt', permission='loggedin')
def achievements_category(request):
    layout = get_renderer('../../templates/layouts/empty.pt').implementation()
    
    return dict(
        title  = "Achievements",
        layout = layout
    )
