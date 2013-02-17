from . import config
from . import api

def add_views(config):
    config.add_route('achievements.admin.player', '/achievements/admin/player/{player_id}')
    config.add_route('achievements.admin.list', '/achievements/admin/list')
    config.add_route('achievements.admin.edit', '/achievements/admin/edit/{achievement_id}')
    config.add_route('achievements.admin.add', '/achievements/admin/add')
    config.add_route('achievements.admin', '/achievements/admin')
    
    config.add_route('achievements.showcase_popup', '/achievements/showcase_popup')
    config.add_route('achievements.dashboard', '/achievements')
    config.add_route('achievements.search', '/achievements/search')
    config.add_route('achievements.category', '/achievements/{user_id}/{category}')
    config.add_route('achievements.sub_category', '/achievements/{user_id}/{category}/{sub_category}')
    config.add_route('achievements.edit_showcase', '/achievements/edit_showcase')
    config.add_route('achievements.user', '/achievements/{user_id}')
    
    return config
