import time

import validators


def sleep(seconds):
    for i in range(seconds):
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            continue

def file_to_list(filename):
    colabs = []
    for line in open(filename):
        if validators.url(line):
            colabs.append(line)
    return colabs

