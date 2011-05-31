#!/usr/bin/env python

__all__ = ['read_tags', 'VideoTags']

from collections import defaultdict

def read_tags():
    """Read the tags associated with video frames in the file videotags.csv."""
    f = open('videotags.csv')
    skip = f.readline()
    tags = defaultdict(lambda: [])
    for line in f:
        fields = line.rstrip().split(',')
        vid = int(fields[0])
        framestart = int(fields[1])
        frameend = None if len(fields[2])==0 else int(fields[2])
        frametags = set(fields[3:])
        tags[vid].append((framestart, frameend, frametags))
    return VideoTags(dict(tags))

class VideoTags(object):
    def __init__(self, tags):
        self.tags = tags

    def frame_tags(self, vid, frame):
        """Find all tags associated with a given video frame."""
        if not self.tags.has_key(vid):
            raise Exception("Video ID not found.")
        v = self.tags[vid]
        L = []
        for interval in v:
            if frame >= interval[0] and frame <= interval[1]:
                L += interval[2]
        return set(L)

    @property
    def videos(self):
        return self.tags.keys()

    @property
    def all_tags(self):
        """The set of all tags as a sorted list."""
        t = list(set.union(*[L[2] for v in self.tags.values() for L in v]))
        t.sort()
        return t

if __name__=='__main__':
    from pprint import pprint
    T = read_tags()
    pprint(T.tags)
    print T.frame_tags(-1546120540, 58200)
    print T.videos
    print T.all_tags
