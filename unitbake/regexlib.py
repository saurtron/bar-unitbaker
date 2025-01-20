import re

splitter_regex = None
line_regex = None

class Match():
    def __init__(self, match, index):
        self._match = match
        self._index = index
    def found(self):
        return self._match != None
    def start(self):
        return self._match.start(self._index)
    def end(self):
        return self._match.end(self._index)
    def full_start(self):
        return self._match.start(0)
    def full_end(self):
        return self._match.end(0)
    def full(self):
        return self._match.group(0)
    def content(self):
        return self._match.group(self._index)
    def __getattr__(self, name):
        if hasattr(self._match, name):
            return getattr(self._match, name)
        raise AttributeError

def create_line_regex():
    global line_regex
    if line_regex:
        return line_regex
    #regex = b'[\s]*?(\\[?[\w\.]+\\]?)[\s]*\=[\s]*(.*),?[\s]*(?:\-\-.*)'
    regex = b'[\s]*?(\\[?[\w\.]+\\]?)[\s]*\=[\s]*(.*),?[\s]*[\-]?[\-]?'
    #regex = b'[\s]*?(\\[?[\w\.]+\\]?)[\s]*[=][\s]*(.*),?'
    pat = re.compile(regex, re.DOTALL)
    line_regex = pat
    return pat

def create_splitter_regex():
    global splitter_regex
    if splitter_regex:
        return splitter_regex
    rawseps = [b'\n', b'\t', b' ', b'\r', b',', b'-']
    preface = b'(?:['+b''.join(rawseps)+b']{1}|^)'
    postface = b'(?:['+b''.join(rawseps)+b']{1}|$)'
    limiters = [b'end', b'do', b'if', b'elseif', b'else', b'function', b'\\(', b'\\)', b'{', b'}']
    limiters = list(map(lambda s: preface+b'('+s+b')'+postface, limiters))
    regex = b'|'.join(limiters)
    regex = b'(--\\[{2}.*?\\]{2})|'+regex+b'|(^[\s]*--.*?$)'
    #print(regex)
    pat = re.compile(regex, re.M | re.DOTALL)
    splitter_regex = pat
    return pat

if __name__ == '__main__':
    run(dest_file, dest_dir)
