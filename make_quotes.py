import re
import yaml
import json
import random
import pandas as pd
from tqdm import tqdm
from pydub import AudioSegment

PATTERN_RE = re.compile('\(([^()]+)\)')

spec = yaml.load(open('tree.yml'))
quotes = json.load(open('data/quotes.json'))
quotes['01_conjunctives'] = yaml.load(open('conjunctives.yml'))
to_filename = yaml.load(open('to_filename.yml'))

def parse_pattern(pattern):
    # Note: doesn't handle nested parentheses
    sequence = []
    if not pattern.startswith('('):
        key = pattern
        sequence += parse_key(key)
    else:
        for part in PATTERN_RE.findall(pattern):
            keys = part.split('|')
            key = random.choice(keys)
            if key != 'null':
                sequence += parse_key(key)
    return sequence

def parse_key(key):
    if key in spec:
        sub_pattern = random.choice(spec[key])
        return parse_pattern(sub_pattern)
    else:
        quote = random.choice(quotes[key])
        quote['key'] = key
        return [quote]

def build_audio(sequence, output):
    segs = []
    for part in sequence:
        hash = part['hash']
        key = part['key']
        fname = to_filename.get(hash, hash)
        path = f'data/GTA5_audio/{key}/{fname}.wav'
        seg = AudioSegment.from_wav(path)
        segs.append(seg)
        segs.append(AudioSegment.silent(duration=random.random() * 500))
    clip = sum(segs)
    clip.export(output, format='wav')

df = {
    'transcript': [],
    'hashes': [],
    'filename': []
}
for i in tqdm(range(1000)):
    fname = f'data/audio/{i}.wav'
    seq = parse_pattern(spec['START'][0])

    transcript = ' '.join([s['quote'] for s in seq])
    hashes = ','.join([s['hash'] for s in seq])
    df['transcript'].append(transcript)
    df['hashes'].append(hashes)
    df['filename'].append(fname.split('/')[-1])
    try:
        build_audio(seq, fname)
    except FileNotFoundError as e:
        print('Failed:', e)
        continue

df = pd.DataFrame(df)
df.to_csv('data/data.csv', index=False)
