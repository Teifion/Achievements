class AUser(object):
    """A simple object to provide an interface into whatever your system User object is.
    It allows us to use property names within the Achievements framework without having
    to know what your User object uses."""
    
    def __init__(self, request_object):
        super(AUser, self).__init__()
        user_object = config['get_user_func'](request_object)
        
        self.id = getattr(user_object, config['user.id_property'])
        self.name = getattr(user_object, config['user.name_property'])

config = {
    "layout": "../templates/default_layout.pt",
    "DBSession": None,
    "User": None,
    
    "get_user_func": lambda r: KeyError("No function exists to get the userid"),
    "get_user": AUser,
}

def example_config_constructor(config):
    """This is an example of how I'm setting up my Concision configuration"""
    
    from . import achievements
    config = achievements.add_views(config)
    achievements.config.config['layout'] = '../../templates/layouts/viewer.pt'
    achievements.config.config['DBSession'] = DBSession
    achievements.config.config['User'] = MyUserModel
    
    achievements.config.config['get_user_func']      = lambda r: r.user
    achievements.config.config['user.id_property']   = "id"
    achievements.config.config['user.name_property'] = "name"
    
    # Additionally I have the following line in my views/__init__.py
    # from ..achievements.views import *
