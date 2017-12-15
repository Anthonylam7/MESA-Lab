from os import walk, getcwd
import re
from kivy.lang.builder import Builder

def load_all_kv():
    pattern = re.compile(".*\.kv")

    for dir, subdirs, files in walk(getcwd()):
        for file in files:
            if pattern.match(file):
                Builder.load_file(dir+'/'+file)

