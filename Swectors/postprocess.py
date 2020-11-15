import sys

for line in sys.stdin:
    words = [w for w in line.rstrip().lower().split() if w.isalpha() and w != 'noword']
    if len(words) > 0:
        print(" ".join(words))
