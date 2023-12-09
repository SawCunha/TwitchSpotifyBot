from enum import Enum


class Permission(Enum):
    ALL = 'all'
    SUBS = 'subs'
    FOLLOWERS = 'followers'
    PRIVILEGED = 'privileged'
