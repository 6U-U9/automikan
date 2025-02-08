import libtorrent

def get_torrent_info_hash(content) -> str:
    info = libtorrent.torrent_info(content)
    return str(info.info_hash())