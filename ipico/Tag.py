from bisect import insort
class TagFactory(type):
    __tag_dict = {}
    class Tag():
        def __init__(self, tag_id):
            def ishex(val):
                try:
                    int(val, 16)
                    return True
                except ValueError:
                    return False

            self.__scans = []

            if(not (isinstance(tag_id, str) and ishex(tag_id)
                    and len(tag_id) == 12)):
                raise ValueError('Argument Tag ID (tag_id) must be a '
                                 '12-character hexadecimal string!')
            self.__id = tag_id

        @property
        def id(self):
            return self.__id

        @property
        def scans(self):
            for s in self.__scans:
                yield s

        @property
        def newest(self):
            if(len(self.__scans) == 1):
                return None
            else:
                return self.__scans[-1]

        def observe(self, scan):
            insort(self.__scans, scan)

        def __str__(self):
            return self.id

        def __hash__(self):
            return int(self.id, 16)

        def __eq__(self, o):
            return self.id == o.id

    @classmethod
    def num_tags(cls):
        return len(cls.__tag_dict.keys())

    @classmethod
    def register_tag(cls, tag_id):
        if tag_id in cls.__tag_dict:
            raise KeyError(f'Tag ID {tag_id} already registered')
        else:
            tag = cls.Tag(tag_id)
            cls.__tag_dict[tag_id] = tag
            return tag
        
    @classmethod
    def scan_tag(cls, tag_id, scan):
        try:
            tag = cls.__tag_dict[tag_id]
        except KeyError:
            tag = cls.Tag(tag_id)
            cls.__tag_dict[tag_id] = tag
        tag.observe(scan)
        return tag
