from pyramid.view import (
    view_config,
)

from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import get_renderer
import datetime

from sqlalchemy import func
import transaction
from .. import achievement_functions
from ..config import config

from ..achievement_models import (
    AchievementSection,
    AchievementCategory,
    AchievementSubCategory,
    AchievementType,
    Achievement,
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
        the_category.description = request.params['description'].strip()
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
        title        = 'Edit category: %s' % the_category.name,
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
    
    type_count = config['DBSession'].query(func.count(AchievementSubCategory.id)).filter(AchievementSubCategory.category == category_id).first()[0]
    
    if type_count > 0:
        layout = get_renderer(config['layout']).implementation()
        
        return dict(
            title           = 'Delete category: %s' % the_category.name,
            the_category = None,
            message         = "This category still has sub categories. You cannot delete it until they are gone.",
            layout          = layout,
        )
    
    editors = achievement_functions.editors_for_category(the_category)
    if the_user.id not in editors:
        layout = get_renderer(config['layout']).implementation()
        
        return dict(
            title                = 'Delete sub category: %s' % the_category.name,
            the_category = None,
            message              = "You are not authorised to delete sub categories in this section",
            layout               = layout,
        )
    
    if 'form.submitted' in request.params:
        with transaction.manager:
            config['DBSession'].delete(the_category)
        
        the_category = AchievementCategory()
        the_category.name = ""
        the_category.id = -1
    
    layout = get_renderer(config['layout']).implementation()
    
    return dict(
        title           = 'Delete sub category: %s' % the_category.name if the_category != None else "Sub category deleted",
        layout          = layout,
        the_category = the_category,
    )

@view_config(route_name='achievements.admin.subcategory.add', renderer='../templates/admin/edit_subcategory.pt', permission='achievements_admin')
@view_config(route_name='achievements.admin.subcategory.edit', renderer='../templates/admin/edit_subcategory.pt', permission='achievements_admin')
def edit_subcategory(request):
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
    if "subcategory_id" not in request.matchdict:
        the_subcategory = AchievementSubCategory()
        the_subcategory.id = -1
        
    else:
        subcategory_id = int(request.matchdict['subcategory_id'])
        if subcategory_id > 0:
            the_subcategory = config['DBSession'].query(AchievementSubCategory).filter(AchievementSubCategory.id == subcategory_id).first()
            
        else:
            the_subcategory        = AchievementSubCategory()
    
    if 'form.submitted' in request.params:
        the_subcategory.name     = request.params['name'].strip()
        the_subcategory.description = request.params['description'].strip()
        the_subcategory.category = int(request.params['category'])
        
        # TODO check editor permissions within this category before adding it to it
        the_subcategory.private = "private" in request.params
        
        config['DBSession'].add(the_subcategory)
        
        message = "Changes saved at %s" % datetime.datetime.now().strftime("%H:%M, on %d of %B")
        
        if the_subcategory.id in (None, -1):
            the_subcategory.id = config['DBSession'].query(AchievementSubCategory.id).filter(AchievementSubCategory.name == the_subcategory.name).order_by(AchievementSubCategory.id.desc()).first()[0]
            
            return HTTPFound(location = request.route_url('achievements.admin.subcategory.edit', subcategory_id=the_subcategory.id))
    
    # Accessible categories
    categories = []
    filters = (
        AchievementCategory.section == AchievementSection.id,
        "{:d} = ANY(achievement_sections.editors)".format(the_user.id),
    )
    for c, s in config['DBSession'].query(AchievementCategory, AchievementSection).filter(*filters).order_by(AchievementSection.name.asc(), AchievementCategory.name.asc()):
        categories.append("<option value='{}' {}>{}: {}</option>".format(
            c.id,
            "selected='selected'" if c.id == int(request.params.get("category", -1)) else "",
            s.name, c.name,
        ))
    
    return dict(
        title           = 'Edit sub category: %s' % the_subcategory.name,
        layout          = layout,
        the_subcategory = the_subcategory,
        message         = message,
        flash_colour    = flash_colour,
        categories      = "".join(categories),
    )

@view_config(route_name='achievements.admin.subcategory.delete', renderer='../templates/admin/delete_subcategory.pt', permission='achievements_admin')
def delete_subcategory(request):
    subcategory_id = int(request.matchdict['subcategory_id'])
    the_subcategory = config['DBSession'].query(AchievementSubCategory).filter(AchievementSubCategory.id == subcategory_id).first()
    the_user = config['get_user'](request)
    
    type_count = config['DBSession'].query(func.count(AchievementType.id)).filter(AchievementType.subcategory == subcategory_id).first()[0]
    
    if type_count > 0:
        layout = get_renderer(config['layout']).implementation()
        
        return dict(
            title           = 'Delete sub category: %s' % the_subcategory.name,
            the_subcategory = None,
            message         = "This subcategory still has achievements in it. You cannot delete it until they are gone.",
            layout          = layout,
        )
    
    editors = achievement_functions.editors_for_subcategory(the_subcategory)
    if the_user.id not in editors:
        layout = get_renderer(config['layout']).implementation()
        
        return dict(
            title                = 'Delete sub category: %s' % the_subcategory.name,
            the_subcategory = None,
            message              = "You are not authorised to delete sub categories in this section",
            layout               = layout,
        )
    
    if 'form.submitted' in request.params:
        with transaction.manager:
            config['DBSession'].delete(the_subcategory)
        
        the_subcategory = AchievementSubCategory()
        the_subcategory.name = ""
        the_subcategory.id = -1
    
    layout = get_renderer(config['layout']).implementation()
    
    return dict(
        title           = 'Delete sub category: %s' % the_subcategory.name if the_subcategory != None else "Sub category deleted",
        layout          = layout,
        the_subcategory = the_subcategory,
    )

@view_config(route_name='achievements.admin.achievement_type.add', renderer='../templates/admin/edit_achievement_type.pt', permission='achievements_admin')
@view_config(route_name='achievements.admin.achievement_type.edit', renderer='../templates/admin/edit_achievement_type.pt', permission='achievements_admin')
def edit_achievement_type(request):
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
    if "achievement_type_id" not in request.matchdict:
        the_achievement_type = AchievementType()
        the_achievement_type.id = -1
        
    else:
        achievement_type_id = int(request.matchdict['achievement_type_id'])
        if achievement_type_id > 0:
            the_achievement_type = config['DBSession'].query(AchievementType).filter(AchievementType.id == achievement_type_id).first()
            
        else:
            the_achievement_type        = AchievementType()
    
    if 'form.submitted' in request.params:
        the_achievement_type.name             = request.params['name'].strip()
        the_achievement_type.label            = request.params['label'].strip()
        the_achievement_type.lookup           = request.params['lookup'].strip()
        
        the_achievement_type.description      = request.params['description'].strip()
        
        try:
            the_achievement_type.points           = int(request.params['points'])
        except Exception:
            the_achievement_type.points = 0
            
        try:
            the_achievement_type.activation_count = int(request.params['activation_count'])
        except Exception:
            the_achievement_type.activation_count = 0
        
        the_achievement_type.private = "private" in request.params
        
        the_achievement_type.subcategory         = int(request.params['subcategory'])
        # TODO check editor permissions within this subcategory before adding it to it
        
        config['DBSession'].add(the_achievement_type)
        
        message = "Changes saved at %s" % datetime.datetime.now().strftime("%H:%M, on %d of %B")
        
        if the_achievement_type.id in (None, -1):
            the_achievement_type.id = config['DBSession'].query(AchievementType.id).filter(AchievementType.name == the_achievement_type.name).order_by(AchievementType.id.desc()).first()[0]
            
            return HTTPFound(location = request.route_url('achievements.admin.achievement_type.edit', achievement_type_id=the_achievement_type.id))
    
    # Accessible subcategories
    subcategories = []
    filters = (
        AchievementCategory.section == AchievementSection.id,
        AchievementSubCategory.category == AchievementCategory.id,
        "{:d} = ANY(achievement_sections.editors)".format(the_user.id),
    )
    for sc, c, s in config['DBSession'].query(AchievementSubCategory, AchievementCategory, AchievementSection).filter(*filters).order_by(AchievementSection.name.asc(), AchievementCategory.name.asc()):
        subcategories.append("<option value='{}' {}>{} {}: {}</option>".format(
            sc.id,
            "selected='selected'" if c.id == int(request.params.get("category", -1)) else "",
            s.name, c.name, sc.name
        ))
    
    return dict(
        title                = 'Edit achievement type: %s' % the_achievement_type.name,
        layout               = layout,
        the_achievement_type = the_achievement_type,
        message              = message,
        flash_colour         = flash_colour,
        subcategories        = "".join(subcategories),
    )

@view_config(route_name='achievements.admin.achievement_type.delete', renderer='../templates/admin/delete_achievement_type.pt', permission='achievements_admin')
def delete_achievement_type(request):
    achievement_type_id = int(request.matchdict['achievement_type_id'])
    the_achievement_type = config['DBSession'].query(AchievementType).filter(AchievementType.id == achievement_type_id).first()
    the_user = config['get_user'](request)
    
    editors = achievement_functions.editors_for_achievement(the_achievement_type)
    if the_user.id not in editors:
        layout = get_renderer(config['layout']).implementation()
        
        return dict(
            title                = 'Delete achievement type: %s' % the_achievement_type.name,
            the_achievement_type = None,
            message              = "You are not authorised to delete achievement types in this section",
            layout               = layout,
        )
    
    if 'form.submitted' in request.params:
        with transaction.manager:
            config['DBSession'].query(Achievement).filter(Achievement.item == achievement_type_id).delete()
            config['DBSession'].delete(the_achievement_type)
        
        the_achievement_type = AchievementType()
        the_achievement_type.name = ""
        the_achievement_type.id = -1
    
    layout = get_renderer(config['layout']).implementation()
    
    return dict(
        title                = 'Delete achievement type: %s' % the_achievement_type.name if the_achievement_type != None else "Achievement type deleted",
        layout               = layout,
        the_achievement_type = the_achievement_type,
    )
