def build_config(config):
    config.add_route('achievements.showcase_popup', '/achievements/showcase_popup')
    config.add_route('achievements.dashboard', '/achievements')
    config.add_route('achievements.search', '/achievements/search')
    config.add_route('achievements.category', '/achievements/{user_id}/{category}')
    config.add_route('achievements.sub_category', '/achievements/{user_id}/{category}/{sub_category}')
    config.add_route('achievements.edit_showcase', '/achievements/edit_showcase')
    config.add_route('achievements.user', '/achievements/{user_id}')
