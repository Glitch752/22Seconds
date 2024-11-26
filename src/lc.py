import glob

lc = lambda x: len(open(x).readlines())

print(f"Current Project Linecount: {sum([lc(x) for x in glob.glob('**/*.py', recursive=True)]) - lc(__file__)}")