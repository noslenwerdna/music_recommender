import numpy as np
from scipy.linalg import circulant

def normalize(vec):
    return (vec - np.average(vec))/np.std(vec)

def find_key(chroma_time):
    # input is vector with 12 rows representing the 12 tone scale.
    # columns represent time.
    # value is the duration of time spent at each tone.
    # found with librosa chroma_stft.

    # this is implementing the Krumhansl-Schmuckler key-finding algorithm
    # ref: http://rnhart.net/articles/key-finding/

    # 1) normalize time spent at each tone
    # 2) normalize tone profile
    # 3) find the duration with the maximum dot product

    # normalize time spent at each tone
    chroma = normalize(np.sum(chroma_time, axis=1))
    tone_labels = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    # normalize tone profiles (found by Krumhansl-Schmuckler)
    major = np.asarray([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
    major = normalize(major)
    minor = np.asarray([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
    minor = normalize(minor)

    # calculate the dot product of all circulants
    major_dot = np.dot(circulant(major).T, chroma)
    minor_dot = np.dot(circulant(minor).T, chroma)
    # pick the maximum
    key = ""
    if np.max(major_dot) >= np.max(minor_dot):
        idx = np.argmax(major_dot)
        key = ("major", tone_labels[idx], idx)
    else:
        idx = np.argmax(minor_dot)
        key = ("minor", tone_labels[idx], idx)

    return key
