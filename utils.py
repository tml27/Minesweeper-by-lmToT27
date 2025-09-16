import os, sys

def p(path):
    return os.path.join(getattr(sys, '_MEIPASS', os.path.abspath(".")), path)