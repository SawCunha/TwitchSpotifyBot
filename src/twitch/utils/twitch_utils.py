from utils.enum.permission import Permission


async def check_permission(user: twitchio.PartialChatter, permission: Permission, channel: str):
    if user.is_broadcaster:
        return True
    if permission is Permission.ALL.name:
        return True
    if permission is Permission.SUBS.name:
        if not user.is_subscriber:
            raise BadPerms('subscriber')
    if permission is Permission.FOLLOWERS.name:
        if not await is_follower(user, channel):
            raise BadPerms('follower')
    if permission is Permission.PRIVILEGED.name:
        if not await is_privileged(user):
            raise BadPerms('mod, subscriber or vip')



async def is_follower(user: twitchio.PartialChatter, channel: str):
    user = await user.user()
    following = await user.fetch_following()
    return channel in [follow.to_user.name.lower() for follow in following]


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
