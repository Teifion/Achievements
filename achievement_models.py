from sqlalchemy import (
    Column,
    DateTime,
    Boolean,
    Integer,
    Interval,
    Text,
    String,
    ForeignKey,
)

from sqlalchemy.dialects.postgresql import (
    ARRAY,
)

from .config import config
from sqlalchemy.orm import relationship

# You will need to point this to wherever your declarative base is
# I'm not yet sure how to remove this requirement
from ..models import Base

class AchievementSection(Base):
    __tablename__ = 'achievement_sections'
    id      = Column(Integer, primary_key=True)
    name    = Column(String, nullable=False, index=True)
    private = Column(Boolean, default=False)
    
    owner   = Column(Integer, ForeignKey("users.id"), nullable=False)
    description   = Column(Text, nullable=False)
    
    # A list of people that can edit this section
    editors = Column(ARRAY(Integer), nullable=False, default=[])

class AchievementCategory(Base):
    __tablename__ = 'achievement_categories'
    id      = Column(Integer, primary_key=True)
    name    = Column(String, nullable=False, index=True)
    private = Column(Boolean, default=False)
    description   = Column(Text, nullable=False)
    
    # Set to -1 if has no parent
    section  = Column(Integer, ForeignKey("achievement_sections.id"), nullable=False, index=True)

class AchievementSubCategory(Base):
    __tablename__ = 'achievement_subcategories'
    id      = Column(Integer, primary_key=True)
    name    = Column(String, nullable=False, index=True)
    private = Column(Boolean, default=False)
    description   = Column(Text, nullable=False)
    
    # Set to -1 if has no parent
    # section  = Column(Integer, ForeignKey("achievement_sections.id"), nullable=False)
    category  = Column(Integer, ForeignKey("achievement_categories.id"), nullable=False, index=True)

class AchievementType(Base):
    __tablename__ = 'achievement_types'
    id            = Column(Integer, primary_key=True)
    
    # This is used when we programatically assign achievements so we can look up
    # the achievement knowing what it's lookup will be and not need to
    # worry about other achievements with the same name
    lookup        = Column(String, nullable=True, unique=True, index=True)
    
    # The name displayed to users
    name  = Column(String, nullable=False)
    
    # The name of a given instance (so the type is 'Best seller' but the label is 'Best seller of X'
    label = Column(String, nullable=False, default="")
    
    # Information about the achievement and how to achieve it. We're putting it
    # as text just incase we want to use a long piece of text
    description   = Column(Text, nullable=False)
    
    points        = Column(Integer, nullable=False)
    
    # How many times must you do something to get the achievement?
    activation_count = Column(Integer, nullable=False, default=0)
    
    # Can't be found by searching, only show if they have the achievement
    private = Column(Boolean, default=False)
    
    # section     = Column(Integer, ForeignKey("achievement_sections.id"), nullable=False)
    # category    = Column(Integer, ForeignKey("achievement_categories.id"), nullable=False)
    subcategory = Column(Integer, ForeignKey("achievement_subcategories.id"), nullable=False, index=True)
    
    achievements = relationship("Achievement")

class Achievement(Base):
    __tablename__ = 'achievements'
    id            = Column(Integer, primary_key=True)
    user          = Column(Integer, ForeignKey("users.id"), nullable=False)
    item          = Column(Integer, ForeignKey("achievement_types.id"), nullable=False)
    
    # Is null until actually awarded
    first_awarded = Column(DateTime, nullable=True)
    last_awarded  = Column(DateTime, nullable=True)
    expires       = Column(DateTime, nullable=True)
    
    activation_count = Column(Integer, nullable=False, default=0)

class AchievementShowcase(Base):
    """A list of the achievements a player is showing in their showcase."""
    __tablename__ = 'achievement_showcase'
    id          = Column(Integer, primary_key=True)
    user        = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    achievement = Column(Integer, ForeignKey("achievement_types.id"), nullable=False)
    placement   = Column(Integer, nullable=False)
