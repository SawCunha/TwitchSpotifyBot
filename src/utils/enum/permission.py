from enum import Enum


def get_permission(permission: str):
    try:
        return Permission[permission.upper()]
    except:
        return Permission.ALL


class Permission(Enum):
    ALL = 'all'
    SUBSCRIBER = 'subscriber'
    FOLLOWERS = 'followers'
    MOD = 'mod'
    VIP = 'vip'
    TURBO = 'turbo'

