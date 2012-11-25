from pyramid.view import (
    view_config,
)

from pyramid.renderers import get_renderer

from . import achievement_functions

from ...models import (
    DBSession,
    AchievementType,
    Achievement,
    AchievementShowcase,
)

@view_config(route_name='achievements_dashboard', renderer='templates/achievement_dashboard.pt', permission='loggedin')
def achievement_dashboard(request):
    layout = get_renderer('../../templates/layouts/empty.pt').implementation()
    
    # Showcase chosen by user
    showcase = DBSession.query(AchievementShowcase.items).filter(AchievementShowcase.user == request.user.id).first()
    if showcase == None: showcase = []
    else: showcase = showcase[0][0:5]
    
    completed = []
    pending = []
    recents = []
    type_ids = set(showcase)
    for a in DBSession.query(Achievement).filter(Achievement.user == request.user.id).order_by(Achievement.first_awarded.desc()):
        if a.first_awarded == None:
            pending.append(a)
        else:
            if len(recents) < 5:
                recents.append(a)
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
        recents = recents,
        showcase = showcase,
        sections = achievement_functions.sections,
    )

@view_config(route_name='achievements_category', renderer='templates/achievements_category.pt', permission='loggedin')
def achievements_category(request):
    layout = get_renderer('../../templates/layouts/empty.pt').implementation()
    
    category = request.matchdict['category']
    
    return dict(
        title  = "Achievements",
        layout = layout,
        category = achievement_functions.sections[category],
        sub_categories = achievement_functions.sections[category]['sub_categories'],
    )

@view_config(route_name='achievements_sub_category', renderer='templates/achievements_sub_category.pt', permission='loggedin')
def achievements_sub_category(request):
    layout = get_renderer('../../templates/layouts/empty.pt').implementation()
    
    user_id = request.matchdict['user_id']
    category = request.matchdict['category']
    sub_category = request.matchdict['sub_category']
    
    achievement_list = []
    achievement_types = []
    
    return dict(
        title  = "Achievements",
        layout = layout,
        category = achievement_functions.sections[category],
        sub_category = achievement_functions.sections[category]['sub_categories'][sub_category],
        user_id = user_id,
        achievement_list = achievement_list,
        achievement_types = achievement_types,
    )

@view_config(route_name='user_achievements', renderer='templates/user_achievements.pt', permission='loggedin')
def user_achievements(request):
    layout = get_renderer('../../templates/layouts/empty.pt').implementation()
    
    return dict(
        title  = "Achievements",
        layout = layout
    )
