from . import config
from . import api

def add_views(config):
    # Ajax
    config.add_route('achievements.ajax.list_categories', '/achievements/ajax/list_categories')
    config.add_route('achievements.ajax.list_subcategories', '/achievements/ajax/list_subcategories')
    config.add_route('achievements.ajax.list_achievement_types', '/achievements/ajax/list_achievement_types')
    
    # Dev
    config.add_route('achievements.dev.section.add', '/achievements/dev/section/add')
    config.add_route('achievements.dev.section.edit', '/achievements/dev/section/edit/{section_id}')
    config.add_route('achievements.dev.section.delete', '/achievements/dev/section/delete/{section_id}')
    config.add_route('achievements.dev', '/achievements/dev')
    
    # Admin
    config.add_route('achievements.admin.category.add', '/achievements/admin/category/add')
    config.add_route('achievements.admin.category.edit', '/achievements/admin/category/edit/{category_id}')
    config.add_route('achievements.admin.category.delete', '/achievements/admin/category/delete/{category_id}')
    
    config.add_route('achievements.admin.subcategory.add', '/achievements/admin/subcategory/add')
    config.add_route('achievements.admin.subcategory.edit', '/achievements/admin/subcategory/edit/{subcategory_id}')
    config.add_route('achievements.admin.subcategory.delete', '/achievements/admin/subcategory/delete/{subcategory_id}')
    
    config.add_route('achievements.admin.achievement_type.add', '/achievements/admin/achievement_type/add')
    config.add_route('achievements.admin.achievement_type.edit', '/achievements/admin/achievement_type/edit/{achievement_type_id}')
    config.add_route('achievements.admin.achievement_type.delete', '/achievements/admin/achievement_type/delete/{achievement_type_id}')
    config.add_route('achievements.admin.achievement_type.overview', '/achievements/admin/achievement_type/overview')
    
    config.add_route('achievements.admin.user', '/achievements/admin/user/{user_id}')
    config.add_route('achievements.admin.user_search', '/achievements/admin/search')
    config.add_route('achievements.admin.achievement.edit', '/achievements/achievement/edit/{achievement_id}')
    
    config.add_route('achievements.admin', '/achievements/admin')
    
    # User
    config.add_route('achievements.showcase_popup', '/achievements/showcase_popup')
    config.add_route('achievements.search', '/achievements/search')
    config.add_route('achievements.section', '/achievements/section/{user_id}/{section_id}')
    config.add_route('achievements.category', '/achievements/category/{user_id}/{category_id}')
    config.add_route('achievements.sub_category', '/achievements/subcategory/{user_id}/{subcategory_id}')
    config.add_route('achievements.edit_showcase', '/achievements/edit_showcase')
    
    config.add_route('achievements.user', '/achievements/{user_id}')
    config.add_route('achievements.dashboard', '/achievements')
    
    return config
