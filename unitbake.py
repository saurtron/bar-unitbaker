import os
import os.path
import sys
import re
import pprint

argv = sys.argv.copy()
do_write = False
dest_file = None
dest_dir = "."
debug = False
debugblocks = False
debugstack = False
debuglocals = False
debugspeedups = False
notfound_files = []

if '-write' in argv:
    do_write = True
    argv.remove('-write')

if '-debug' in argv:
    debug = True
    argv.remove('-debug')

if '-debugblocks' in argv:
    debugblocks = True
    argv.remove('-debugblocks')

if '-debugstack' in argv:
    debugstack = True
    argv.remove('-debugstack')
if '-debuglocals' in argv:
    debuglocals = True
    argv.remove('-debuglocals')
if '-debugspeedups' in argv:
    debugspeedups = True
    argv.remove('-debugspeedups')


if len(argv) > 1:
    dest = argv[1]
    if os.path.isfile(dest):
        dest_file = dest
    elif os.path.isdir(dest):
        dest_dir = dest
    else:
        raise "Bad destination"

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

def find_stack_add(elmt):
    if elmt in [b'end', b'}', b')']:
        return -1
    if elmt in [b'do', b'if', b'function', b'{', b'(']:
        return 1
    return 0

def find_block_limits(data, pos, name, endidx=None):
    #print("STACKS", file, data[pos:pos+15], name)
    pat = create_splitter_regex()
    stack = 1
    end1 = False
    end1_end = False
    last_start = None
    first_brace = None
    blocks = {}
    block_starts = {}
    while m := pat.search(data, pos):
        m_index = m.lastindex
        pos = m.end(m_index)
        last_start = m.start(m_index)
        next_elmt = m.group(m_index)
        match = Match(m, m_index)
        if next_elmt == b'{':
            if not first_brace:
                first_brace = last_start
            blocks[last_start] = next_elmt
            block_starts[stack] = last_start
        stack_add = find_stack_add(next_elmt)
        stack = stack + stack_add
        if next_elmt == b'}':
            blocks[block_starts[stack]] = last_start
        if endidx != None and pos > endidx:
            raise "wtf"
        if stack == 0:
            break
    return blocks, first_brace

def all_lines(data, blocks, block_pos):
    lines = []
    regex = b'(\n)'
    pos = block_pos
    pat = re.compile(regex, re.M | re.DOTALL)
    while m := pat.search(data, pos):
        pos = m.end(m.lastindex)
        if pos > blocks[block_pos]+1:
            return lines
        lines.append(pos)
    return lines

def process_line(data, line_orig, line_pos, line_end, units, stack, path, all_attrs):
    line = line_orig.strip(b"\r\n\t")
    pat = create_line_regex()
    m = pat.search(line)
    if m:
        name = m.group(1)
        value = m.group(2)
        new_elmt = False
        if value == b"{":
            value = {}
            new_elmt = True
        elmt = units
        for p in path:
            elmt = elmt[p]
        name_downcase = name.lower()
        elmt[name_downcase] = value
        all_attrs[tuple(path+[name_downcase])] = [line_pos, line_end]
        if new_elmt:
            stack = stack + 1
            path.append(name_downcase)
    elif b'}' in line:
            all_attrs[tuple(path)][1] = line_end
            stack = stack - 1
            path.pop()
    return stack

def process_block(data, blocks, block_pos, units, all_attrs):
    lines = all_lines(data, blocks, block_pos)
    stack = 0
    path = []
    for idx, pos in enumerate(lines[:-1]):
        line = data[pos:lines[idx+1]]
        line_end = lines[idx+1]
        stack = process_line(data, line, pos, line_end, units, stack, path, all_attrs)
        if not path:
            # no unit was found
            return

def process_data(data, file_path, all_units, all_paths, all_attrs):
    if not data.startswith(b'return {'):
        if not b'return {' in data:
            print("No return", file_path)
        else:
            print("Not starts with return", file_path)
        notfound_files.append(os.path.basename(file_path))
        return {}
    units = {}
    blocks, first_brace = find_block_limits(data, 0, 'blocks')
    process_block(data, blocks, first_brace, units, all_attrs)
    for unit_name, unit_data in units.items():
        if unit_name in all_units:
            raise Exception("already have unit!!")
        else:
            all_units[unit_name] = unit_data
            all_paths[unit_name] = file_path
    return units

def process_file(file_path, cb, *args):
    data = None
    with open(file_path, "rb") as f:
        curr_idx = 0
        data = f.read()
        units = cb(data, file_path, *args)

def walk_file(dest_file, cb, *args):
    cb(dest_file, *args)

def walk_dir(dest_dir, cb, *args):
    for path,subdir,files in os.walk(dest_dir):
        for file in files:
            if file.endswith(".lua") and not ".git" in path:
                file_path = os.path.join(path, file)
                cb(file_path, *args)

def apply_op_rm(data, path, val, line_start, attr_end, all_attrs):
    line_end = data.find(b'\n', line_start) + 1
    return data[:line_start]+data[line_end:]

def format_dict(dict_val, preface):
    lines = []
    for name, val in dict_val.items():
        lines.append(preface + name + b' = ' + val.strip(b',') + b',')
    return lines

def format_attribute(path, val, preface):
    name = path[-1]
    lines = []
    if isinstance(val, dict):
        line = preface + name + b' = {'
        lines.append(line)
        lines = lines + format_dict(val, preface + b'\t')
        lines.append(preface + b'},')
    else:
        line = preface + name + b' = ' + val.strip(b',') + b','
        lines.append(line)
    return b'\r\n'.join(lines)+b'\r\n'

def parse_line_attr(line):
    m = re.match(b'.*=[\s]*([\w\"\-]*),?', line, re.DOTALL)
    if not m:
        print("cant find!!!", line)
    val_start = m.start(1)
    val_end = m.end(1)
    ending = line[val_end:]
    return val_start, ending, m

def apply_op_add(data, path, val, line_start, prev_line_start, all_attrs):
    line_end = data.find(b'\n', line_start)
    line = data[line_start:line_end]
    if prev_line_start:
        prev_line_end = data.find(b'\n', prev_line_start)+1
        preface_line = data[prev_line_start:prev_line_end]
    else:
        preface_line = line
    # TODO: check comments!
    m = re.match(b'[\s]*(.*)=.*', preface_line, re.DOTALL)
    if not m:
        print("cant find!!!", preface_line)
    val_start = m.start(1)
    val_end = m.end(1)
    preface = preface_line[:val_start]
    attr = format_attribute(path, val, preface)
    if prev_line_start:
        val_start, ending, m = parse_line_attr(preface_line)
        if not ending.startswith(b','):
            ending = b',' + ending
        new_val = m.group(1)+ending
        val_start = val_start+prev_line_start
        data = data[:val_start]+new_val+attr+data[line_start:]
    else:
        data = data[:line_start]+attr+data[line_start:]
    return data


def apply_op_change(data, path, val, line_start, attr_end, all_attrs):
    line_end = data.find(b'\n', line_start)
    line = data[line_start:line_end]
    # TODO: check comments!
    val_start, ending, m = parse_line_attr(preface_line)
    new_val = val.strip(b',')+ending
    old_val = line[val_start:]
    val_start = val_start+line_start
    data = data[:val_start]+new_val+data[val_start+len(old_val):]
    return data

def apply_diff_operations(data, ops, all_attrs):
    for op, path, val, line_start, attr_end in ops:
        if op == b'd':
            data = apply_op_change(data, path, val, line_start, attr_end, all_attrs)
        elif op == b'-':
            data = apply_op_rm(data, path, val, line_start, attr_end, all_attrs)
        elif op == b'+':
            print(path, val)
            data = apply_op_add(data, path, val, line_start, attr_end, all_attrs)
    return data
     
def find_insertion_pos(path, all_attrs):
    parent_path = path[:-1]
    children = filter(lambda s: len(s) == len(path) and s[:-1] == parent_path, all_attrs)
    last_path = path[-1]
    prev_child = parent_path
    last_child = None
    for child in children:
        if child[-1] > last_path:
            return all_attrs[child][0], None
        last_child = child
    return (all_attrs[child][1], all_attrs[last_child][0])
    # TODO: find next same level as parent?
    raise Exception("Can't find location")

def apply_diff(unit_name, diff_data, file_path, all_attrs):
    ops = []
    add_ops = []
    for path_s, operation in diff_data.items():
        op, val = operation
        # TODO find path for additions
        if path_s:
            path = tuple([unit_name] + path_s.split(b"/"))
        if op == b'+':
            add_ops.append((path_s, path, val))
        else:
            linen = all_attrs[path][0]
            line_end = all_attrs[path][1]
            ops.append((op, path, val, linen, line_end))
    add_ops.sort(key=lambda s: s[0])
    for path_s, path, val in add_ops:
        linen, next_line = find_insertion_pos(path, all_attrs)
        ops.append((b'+', path, val, linen, next_line))
    ops.sort(key=lambda s: -s[3])
    with open(file_path, 'rb') as f:
        data = f.read()
        new_data = apply_diff_operations(data, ops, all_attrs)
        with open(file_path, 'wb') as f:
            f.write(new_data)

def find_diff(d1, d2, path, diff_dict):
    for k in d1:
        if k in d2:
            if type(d1[k]) is dict:
                find_diff(d1[k],d2[k], b"%s/%s" % (path, k) if path else k, diff_dict)
            elif d1[k] != d2[k] and d1[k].strip(b',') != d2[k].strip(b','):
                result = [ "%s: " % path, " - %s : %s" % (k, d1[k]) , " + %s : %s" % (k, d2[k])]
                diff_dict[b"%s/%s" % (path, k) if path else k] = (b'd', d2[k])
        else:
            diff_dict[b"%s/%s" % (path, k) if path else k] = (b'-', d1[k])
    for k in d2:
        if not k in d1:
            diff_dict[b"%s/%s" % (path, k) if path else k] = (b'+', d2[k])


def run_apply_diffs(path, diff_dict, unit_paths, all_attrs):
    for unit_name, diff_data in diff_dict.items():
        if unit_name in unit_paths:
            apply_diff(unit_name, diff_data, unit_paths[unit_name], all_attrs)
        else:
            print(unit_name, "not found!")

def run(dest_file, dest_dir):
    all_units = {}
    all_paths = {}
    all_attrs = {}
    if dest_file:
        walk_file(dest_file, process_file, process_data, all_units, all_paths, all_attrs)
    else:
        walk_dir(dest_dir, process_file, process_data, all_units, all_paths, all_attrs)
    if notfound_files:
        print("NOT FOUND", notfound_files)
    return all_units, all_paths, all_attrs


if __name__ == '__main__':
    run(dest_file, dest_dir)
