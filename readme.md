This set of functions and views is designed to be used in conjunction with the other games I've made. It's also designed to be easy to extend into your own games/systems.

    config.add_route('achievements_dashboard', '/achievements')
    config.add_route('user_achievements', '/achievements/{user_id}')
    config.add_route('achievements_category', '/achievements/{user_id}/{category}')
    config.add_route('achievements_sub_category', '/achievements/{user_id}/{category}/{sub_category}')