#!/usr/bin/env python3

from functools import partial
import pickle
import pandas as pd
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
import matplotlib.style as ms
import key
ms.use("seaborn-muted")


def plots(
    y_h=None, 
    y_p=None, 
    sr=None,
    short_fn=None,
    start_pos=None,
    time_stamp=None
    ):

    fig = plt.figure(figsize=(12,8))
    C = librosa.feature.chroma_cqt(y=y_h, sr=sr, n_chroma=12)
    librosa.display.specshow(C, x_axis="time", y_axis="chroma", sr=sr)
    plt.colorbar()
    plt.title("chroma, " + short_fn + ", start_pos={0}".format(start_pos))
    plt.savefig("data/" + str(time_stamp) + "_chroma.png")
    plt.clf()

    db = librosa.amplitude_to_db(librosa.stft(y_h), np.max)
    librosa.display.specshow(db, x_axis="time", y_axis="log")
    plt.colorbar(format="%+2.0f dB")
    plt.title("harmonic log power spec, " + short_fn + ", start_pos={0}".format(start_pos))
    plt.savefig("data/" + str(time_stamp) + "_harmonic.png")
    plt.clf()

    db = librosa.amplitude_to_db(librosa.stft(y_p), np.max)
    librosa.display.specshow(db, x_axis="time", y_axis="log")
    plt.colorbar(format="%+2.0f dB")
    plt.title("percussive power spec, " + short_fn + ", start_pos={0}".format(start_pos))
    plt.savefig("data/" + str(time_stamp) + "_percussive.png")
    plt.clf()

def get_features(
    fn=None, 
    short_fn=None,
    start_pos=None,
    window=None,
    time_stamp=None
    ):

    # retrieve amplitudes
    y, sr = librosa.load(fn, offset=start_pos, duration=window, sr=None)
    # separate into harmonic and percussive components
    y_h, y_p = librosa.effects.hpss(y)
    # make plots
    plots(
        y_h=y_h,
        y_p=y_p,
        sr=sr,
        short_fn=short_fn,
        start_pos=start_pos,
        time_stamp=time_stamp
    )
    # get simple features
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

    key = key.find_key(librosa.feature.chroma_cqt(y=y_h, sr=sr, n_chroma=12))

    # save
    data = {
        "y": y,
        "sr": sr
    }
    pickle.dump(data, open("data/" + "amp_sr_{0}.pkl".format(time_stamp), "wb"))

    return tempo, key

def enrich_music(df):

    tempo, key = df.apply(lambda x: 
        get_features(
            fn=x.file_name, 
            short_fn=x.short_file_name, 
            start_pos=x.start_position, 
            window=x.play_window,
            time_stamp=x.time_stamp
        ), 
        axis=1)

    return df.assign(tempo=tempo, key=key[0], key_tone=key[1])

if __name__ == "__main__":
    df = pd.read_csv("like_record.tsv", sep="\t")
    df = enrich_music(df)
    pickle.dump(df, open("data/enrich_like_record.pkl", "wb"))
