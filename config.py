config = {
    "layout": "../templates/default_layout.pt",
    "DBSession": None,
    "User": None,
}

def example_config_constructor(config):
    """This is an example of how I'm setting up my Concision configuration"""
    
    from . import achievements
    config = achievements.add_views(config)
    achievements.config.config['layout'] = '../../templates/layouts/viewer.pt'
    achievements.config.config['DBSession'] = DBSession
    achievements.config.config['User'] = MyUserModel
    
    # Additionally I have the following line in my views/__init__.py
    # from ..achievements.views import *
