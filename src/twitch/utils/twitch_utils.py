import twitchio

from utils.db_handler import DB
from utils.errors import *
from utils.enum.permission import Permission


def target_finder(db: DB, request: str) -> str:
    words = request.split(' ')
    for word in words:
        if word.startswith('@'):
            target = word
            target = target.strip('@')
            target = target.strip('\n')
            target = target.strip('\r')
            target = target.strip(' ')
            db.check_user_exists(target)
            return target
    raise TargetNotFound


def time_finder(request: str) -> dict:
    units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
    for unit in units.keys():
        if unit in request:
            try:
                time = int(request.strip(unit))
            except ValueError:
                raise TimeNotFound
            return {'time': time, 'unit': unit}
    # if no unit is found, default to minutes
    unit = 'm'
    request = request.strip(unit)
    try:
        time = int(request)
    except ValueError:
        raise TimeNotFound
    return {'time': time, 'unit': unit}


async def check_permission(user: twitchio.PartialChatter, permission: Permission, channel: str,
                           is_user_privileged: bool):
    if user.is_broadcaster:
        return
    if permission is Permission.SUBS:
        if not user.is_subscriber:
            raise BadPerms('subscriber')
    if permission is Permission.FOLLOWERS:
        if not await is_follower(user, channel):
            raise BadPerms('follower')
    if permission is Permission.PRIVILEGED:
        if not await is_privileged(user):
            raise BadPerms('mod, subscriber or vip')


async def is_follower(user: twitchio.PartialChatter, channel: str):
    user = await user.user()
    following = await user.fetch_following()
    is_follower = channel in [follow.to_user.name.lower() for follow in following]
    return is_follower


async def is_privileged(user: twitchio.PartialChatter, is_user_privileged: bool):
    if is_user_privileged:
        return True
    elif user.is_vip:
        return True
    elif user.is_mod:
        return True
    elif user.is_subscriber:
        return True
    else:
        return False
