from pyramid.view import view_config

from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import get_renderer
from sqlalchemy import func
import datetime
import transaction

from .. import achievement_functions
from ..config import config

from ..achievement_models import (
    AchievementSection,
    AchievementType,
    Achievement,
    AchievementShowcase,
    AchievementCategory,
)

@view_config(route_name='achievements.dev', renderer='../templates/dev/home.pt', permission='achievements_dev')
def dev_dashboard(request):
    layout = get_renderer(config['layout']).implementation()
    
    sections = config['DBSession'].query(AchievementSection).order_by(AchievementSection.name.asc())
    
    return dict(
        title  = "Achievements Dev Home",
        layout = layout,
        sections = list(sections),
    )

@view_config(route_name='achievements.dev.section.add', renderer='../templates/dev/edit_section.pt', permission='achievements_dev')
@view_config(route_name='achievements.dev.section.edit', renderer='../templates/dev/edit_section.pt', permission='achievements_dev')
def edit_section(request):
    layout = get_renderer(config['layout']).implementation()
    message = ""
    flash_colour = "0A0"
    the_user = config['get_user'](request)
    
    # These are used to reference user properties
    attrs = (
        getattr(config['User'], config['user.id_property']),
        getattr(config['User'], config['user.name_property'])
    )
    
    # No submission, we need to grab the existing section
    if "section_id" not in request.matchdict:
        the_section = AchievementSection()
        the_section.id = -1
        
        the_section.owner   = the_user.id
        the_section.editors = [the_user.id]
    else:
        section_id = int(request.matchdict['section_id'])
        if section_id > 0:
            the_section = config['DBSession'].query(AchievementSection).filter(AchievementSection.id == section_id).first()
            
        else:
            the_section        = AchievementSection()
            the_section.owner = the_user.id
    
    if 'form.submitted' in request.params:
        the_section.name        = request.params['name'].strip()
        the_section.description = request.params['description'].strip()
        the_section.private     = "private" in request.params
        
        # Convert editor names into user_ids
        editor_names = []
        for n in request.params['editors'].replace(",", " ").split(" "):
            n = n.strip()
            if n == "": continue
            
            # Our names are all in uppercase, I've not worked out the best way
            # to not have that requirement in the code yet :(
            editor_names.append(n.upper())
        editor_names = [e.strip().upper() for e in editor_names]
        
        the_section.editors = [the_section.owner]
        for u in config['DBSession'].query(attrs[0]).filter(attrs[1].in_(editor_names)):
            the_section.editors.append(u[0])
        
        the_section.editors.append(the_section.owner)
        the_section.editors = tuple(set(the_section.editors))
        
        config['DBSession'].add(the_section)
        
        message = "Changes saved at %s" % datetime.datetime.now().strftime("%H:%M, on %d of %B")
        
        if the_section.id in (None, -1):
            the_section.id = config['DBSession'].query(AchievementSection.id).filter(AchievementSection.name == the_section.name).order_by(AchievementSection.id.desc()).first()[0]
            
            return HTTPFound(location = request.route_url('achievements.dev.section.edit', section_id=the_section.id))
        
    # Usernames
    user_names = {}
    
    for u in config['DBSession'].query(*attrs).filter(attrs[0].in_(the_section.editors)):
        user_names[u.id] = u.name
    
    return dict(
        title        = 'Edit section: %s' % the_section.name,
        layout       = layout,
        the_section  = the_section,
        message      = message,
        flash_colour = flash_colour,
        user_names   = user_names,
    )

@view_config(route_name='achievements.dev.section.delete', renderer='../templates/dev/delete_section.pt', permission='achievements_dev')
def delete_section(request):
    section_id = int(request.matchdict['section_id'])
    the_section = config['DBSession'].query(AchievementSection).filter(AchievementSection.id == section_id).first()
    the_user = config['get_user'](request)
    
    category_count = config['DBSession'].query(func.count(AchievementCategory.id)).filter(AchievementCategory.section == section_id).first()[0]
    
    if category_count > 0:
        layout = get_renderer(config['layout']).implementation()
        
        return dict(
            title       = 'Delete section: %s' % the_section.name,
            the_section = None,
            message     = "This section still has sub categories. You cannot delete it until they are gone.",
            layout      = layout,
        )
    
    if the_section.owner != the_user.id:
        layout = get_renderer('../templates/layouts/viewer.pt').implementation()
        
        return dict(
            title       = 'Edit section: %s' % the_section.name,
            the_section = None,
            message     = "Only the owner can delete a section",
            layout      = layout,
        )
    
    if 'form.submitted' in request.params:
        with transaction.manager:
            config['DBSession'].delete(the_section)
        
        the_section = AchievementSection()
        the_section.name = ""
        the_section.id = -1
    
    layout = get_renderer(config['layout']).implementation()
    
    return dict(
        title        = 'Delete document: %s' % the_section.name if the_section != None else "Doc deleted",
        layout       = layout,
        the_section      = the_section,
    )
