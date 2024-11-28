import glob
from os import path

lc = lambda x: len(open(x).readlines())

pattern = path.normpath(path.join(path.dirname(__file__), "..", "src") + '/**/*.py')
print(f"Current Project Linecount: {sum([lc(x) for x in glob.glob(pattern, recursive=True)])}")