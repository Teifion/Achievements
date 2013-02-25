from . import config
from . import api

def add_views(config):
    # Dev
    config.add_route('achievements.dev.section.add', '/achievements/dev/section/add')
    config.add_route('achievements.dev.section.edit', '/achievements/dev/section/edit/{section_id}')
    config.add_route('achievements.dev.section.delete', '/achievements/dev/section/delete/{section_id}')
    config.add_route('achievements.dev', '/achievements/dev')
    
    # Admin
    config.add_route('achievements.admin.category.add', '/achievements/admin/category/add')
    config.add_route('achievements.admin.category.edit', '/achievements/admin/category/edit/{category_id}')
    config.add_route('achievements.admin.subcategory.add', '/achievements/admin/subcategory/add')
    config.add_route('achievements.admin.subcategory.edit', '/achievements/admin/subcategory/edit/{category_id}')
    config.add_route('achievements.admin.achievement.add', '/achievements/admin/achievement/add')
    config.add_route('achievements.admin.achievement.edit', '/achievements/admin/achievement/edit/{category_id}')
    config.add_route('achievements.admin', '/achievements/admin')
    
    # User
    config.add_route('achievements.showcase_popup', '/achievements/showcase_popup')
    config.add_route('achievements.dashboard', '/achievements')
    config.add_route('achievements.search', '/achievements/search')
    config.add_route('achievements.category', '/achievements/{user_id}/{category}')
    config.add_route('achievements.sub_category', '/achievements/{user_id}/{category}/{sub_category}')
    config.add_route('achievements.edit_showcase', '/achievements/edit_showcase')
    config.add_route('achievements.user', '/achievements/{user_id}')
    
    return config
