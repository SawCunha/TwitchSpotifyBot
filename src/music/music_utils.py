
LINKS_YOUTUBE: [] = ['https://www.youtube.com', 'https://youtu.be/']
LINKS_SPOTIFY: [] = ['open.spotify.com/track', 'open.spotify.com/intl-pt/track']
LINKS_SPOTIFY_TRACK: [] = ['spotify:track:']


def is_spotify_link(request: str):
    if any(link in request for link in LINKS_YOUTUBE):
        return False

    elif 'http:' in request:
        return False

    if any(link in request for link in LINKS_SPOTIFY):
        return True

    if any(link in request for link in LINKS_SPOTIFY_TRACK):
        return True

    return False


def process_spotify_link(request: str):
    if any(link in request for link in LINKS_SPOTIFY):
        link = request
        link = link.strip('\r')
        link = link.strip('\n')
        link = link.replace('/intl-pt', '')
        return link

    elif any(link in request for link in LINKS_SPOTIFY_TRACK):
        link = request
        link = link.strip('\r')
        link = link.strip('\n')
        return link
    return None
