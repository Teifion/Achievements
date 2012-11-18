from sqlalchemy import (
    Column,
    Boolean,
    DateTime,
    Integer,
    Interval,
    Text,
    String,
    ForeignKey,
)

# You will need to point this to wherever your declarative base is
from ...models import Base

class AchievementType(Base):
    __tablename__ = 'achievement_types'
    id            = Column(Integer, primary_key=True)
    
    # The name used to look it up
    lookup        = Column(String, nullable=False, unique=True, index=True)
    
    # The name displayed to users
    name          = Column(String, nullable=False)
    description   = Column(Text, nullable=False)
    points        = Column(Integer, nullable=False)
    
    # How many times must you do something to get the achievement?
    activation_count = Column(Integer, nullable=False, default=0)
    
    # Some achievements expire after a certain amount of time
    duration = Column(Interval, nullable=True)
    
    def __init__(self, lookup, name, description, points=0, activation_count=1, duration=None):
        self.lookup            = lookup
        self.name              = name
        self.description       = description
        self.points            = points
        self.activation_count  = activation_count
        self.duration          = duration

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
