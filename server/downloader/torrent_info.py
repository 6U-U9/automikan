class TorrentInfo:
    path: str
    finish: bool
    
    def __init__(self, path = "", finish = False):
        self.path = path
        self.finish = finish

    def __getitem__(self, key):
        return self.__dict__[key]