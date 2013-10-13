class Anime:
    def __init__(self, **kwargs):
        self.id = 0
        self.has_id = False
        self.title = ""
        self.has_title = False
        self.synonyms = []
        self.has_synonyms = False
        self.type = 0
        self.has_type = False
        self.episode_count = 0
        self.has_episode_count = False
        self.status = 0
        self.has_status = False
        self.start = 0
        self.has_start = False
        self.end = 0
        self.has_end = False