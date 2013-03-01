from pyramid.view import (
    view_config,
)

from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import get_renderer
import datetime

import transaction
from .. import achievement_functions
from ..config import config

from ..achievement_models import (
    AchievementSection,
    AchievementCategory,
    AchievementSubCategory,
)

@view_config(route_name='achievements.admin', renderer='../templates/admin/home.pt', permission='achievements_admin')
def admin_home(request):
    layout = get_renderer(config['layout']).implementation()
    the_user = config['get_user'](request)
    
    where = "{:d} = ANY (achievement_sections.editors)".format(the_user.id)
    sections = config['DBSession'].query(AchievementSection).filter(where).order_by(AchievementSection.name.asc())
    
    return dict(
        title  = "Achievements Admin Home",
        layout = layout,
        sections = list(sections),
    )

@view_config(route_name='achievements.admin.category.add', renderer='../templates/admin/edit_category.pt', permission='achievements_admin')
@view_config(route_name='achievements.admin.category.edit', renderer='../templates/admin/edit_category.pt', permission='achievements_admin')
def edit_category(request):
    layout = get_renderer(config['layout']).implementation()
    message = ""
    flash_colour = "0A0"
    the_user = config['get_user'](request)
    
    # These are used to reference user properties
    # attrs = (
    #     getattr(config['User'], config['user.id_property']),
    #     getattr(config['User'], config['user.name_property'])
    # )
    
    # No submission, we need to grab the existing section
    if "category_id" not in request.matchdict:
        the_category = AchievementCategory()
        the_category.id = -1
        
    else:
        category_id = int(request.matchdict['category_id'])
        if category_id > 0:
            the_category = config['DBSession'].query(AchievementCategory).filter(AchievementCategory.id == category_id).first()
            
        else:
            the_category        = AchievementCategory()
    
    if 'form.submitted' in request.params:
        the_category.name    = request.params['name'].strip()
        the_category.section = int(request.params['section'])
        # TODO check editor permissions within this section before adding it to it
        the_category.private = "private" in request.params
        
        config['DBSession'].add(the_category)
        
        message = "Changes saved at %s" % datetime.datetime.now().strftime("%H:%M, on %d of %B")
        
        if the_category.id in (None, -1):
            the_category.id = config['DBSession'].query(AchievementCategory.id).filter(AchievementCategory.name == the_category.name).order_by(AchievementCategory.id.desc()).first()[0]
            
            return HTTPFound(location = request.route_url('achievements.admin.category.edit', category_id=the_category.id))
    
    # Accessible sections
    sections = []
    for i, n in config['DBSession'].query(AchievementSection.id, AchievementSection.name).filter("{:d} = ANY(achievement_sections.editors)".format(the_user.id)).order_by(AchievementSection.name.asc()):
        sections.append("<option value='{}' {}>{}</option>".format(
            i,
            "selected='selected'" if i == int(request.params.get("section", -1)) else "",
            n,
        ))
    
    return dict(
        title        = 'Edit section: %s' % the_category.name,
        layout       = layout,
        the_category  = the_category,
        message      = message,
        flash_colour = flash_colour,
        sections     = "".join(sections),
    )

@view_config(route_name='achievements.admin.category.delete', renderer='../templates/admin/delete_category.pt', permission='achievements_admin')
def delete_category(request):
    category_id = int(request.matchdict['category_id'])
    the_category = config['DBSession'].query(AchievementCategory).filter(AchievementCategory.id == category_id).first()
    the_user = config['get_user'](request)
    
    if the_category.owner != the_user.id:
        layout = get_renderer('../templates/layouts/viewer.pt').implementation()
        
        return dict(
            title       = 'Edit section: %s' % the_category.name,
            the_category = None,
            message     = "Only the owner can delete a section",
            layout      = layout,
        )
    
    if 'form.submitted' in request.params:
        with transaction.manager:
            config['DBSession'].delete(the_category)
        
        the_category = AchievementCategory()
        the_category.name = ""
        the_category.id = -1
    
    layout = get_renderer(config['layout']).implementation()
    
    return dict(
        title        = 'Delete document: %s' % the_category.name if the_category != None else "Doc deleted",
        layout       = layout,
        the_category      = the_category,
    )

@view_config(route_name='achievements.admin.subcategory.add', renderer='../templates/admin/edit_subcategory.pt', permission='achievements_admin')
@view_config(route_name='achievements.admin.subcategory.edit', renderer='../templates/admin/edit_subcategory.pt', permission='achievements_admin')
def edit_subcategory(request):
    layout = get_renderer(config['layout']).implementation()
    message = ""
    flash_colour = "0A0"
    the_user = config['get_user'](request)
    
    # These are used to reference user properties
    attrs = (
        getattr(config['User'], config['user.id_property']),
        getattr(config['User'], config['user.name_property'])
    )
    
    # No submission, we need to grab the existing subcategory
    if "subcategory_id" not in request.matchdict:
        the_subcategory = AchievementSubCategory()
        the_subcategory.id = -1
        
        the_subcategory.owner   = the_user.id
        the_subcategory.editors = [the_user.id]
    else:
        subcategory_id = int(request.matchdict['subcategory_id'])
        if subcategory_id > 0:
            the_subcategory = config['DBSession'].query(AchievementSubCategory).filter(AchievementSubCategory.id == subcategory_id).first()
            
        else:
            the_subcategory        = AchievementSubCategory()
            the_subcategory.owner = the_user.id
    
    if 'form.submitted' in request.params:
        the_subcategory.name    = request.params['name'].strip()
        the_subcategory.private = "private" in request.params
        
        # Convert editor names into user_ids
        editor_names = []
        for n in request.params['editors'].replace(",", " ").split(" "):
            n = n.strip()
            if n == "": continue
            
            # Our names are all in uppercase, I've not worked out the best way
            # to not have that requirement in the code yet :(
            editor_names.append(n.upper())
        editor_names = [e.strip().upper() for e in editor_names]
        
        the_subcategory.editors = [the_subcategory.owner]
        for u in config['DBSession'].query(attrs[0]).filter(attrs[1].in_(editor_names)):
            the_subcategory.editors.append(u[0])
        
        the_subcategory.editors.append(the_subcategory.owner)
        the_subcategory.editors = tuple(set(the_subcategory.editors))
        
        config['DBSession'].add(the_subcategory)
        
        message = "Changes saved at %s" % datetime.datetime.now().strftime("%H:%M, on %d of %B")
        
        if the_subcategory.id in (None, -1):
            the_subcategory.id = config['DBSession'].query(AchievementSubCategory.id).filter(AchievementSubCategory.name == the_subcategory.name).order_by(AchievementSubCategory.id.desc()).first()[0]
            
            return HTTPFound(location = request.route_url('achievements.admin.subcategory.edit', subcategory_id=the_subcategory.id))
        
    # Usernames
    user_names = {}
    
    for u in config['DBSession'].query(*attrs).filter(attrs[0].in_(the_subcategory.editors)):
        user_names[u.id] = u.name
    
    return dict(
        title           = 'Edit subcategory: %s' % the_subcategory.name,
        layout          = layout,
        the_subcategory = the_subcategory,
        message         = message,
        flash_colour    = flash_colour,
        user_names      = user_names,
    )

@view_config(route_name='achievements.admin.subcategory.delete', renderer='../templates/admin/delete_subcategory.pt', permission='achievements_admin')
def delete_subcategory(request):
    subcategory_id = int(request.matchdict['subcategory_id'])
    the_subcategory = config['DBSession'].query(AchievementSubCategory).filter(AchievementSubCategory.id == subcategory_id).first()
    the_user = config['get_user'](request)
    
    if the_subcategory.owner != the_user.id:
        layout = get_renderer('../templates/layouts/viewer.pt').implementation()
        
        return dict(
            title       = 'Edit subcategory: %s' % the_subcategory.name,
            the_subcategory = None,
            message     = "Only the owner can delete a subcategory",
            layout      = layout,
        )
    
    if 'form.submitted' in request.params:
        with transaction.manager:
            config['DBSession'].delete(the_subcategory)
        
        the_subcategory = AchievementSubCategory()
        the_subcategory.name = ""
        the_subcategory.id = -1
    
    layout = get_renderer(config['layout']).implementation()
    
    return dict(
        title        = 'Delete document: %s' % the_subcategory.name if the_subcategory != None else "Doc deleted",
        layout       = layout,
        the_subcategory      = the_subcategory,
    )
