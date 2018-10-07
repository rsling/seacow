# -*- coding: utf-8 -*-

import itertools

def cow_rough_region_to_conc(region):
  result = list(region)
  del result[1::2]
  return [r.strip() for r in result]


def isplit(iterable, splitters):
  return [list(g) for k,g in itertools.groupby(iterable, lambda x: x in splitters)]

flatten = lambda l: [item for sublist in l for item in sublist]

# Format a Manatee region as raw concordance line.
def cow_region_to_conc(region, attrs = True):
  if not attrs:
    conc = filter(lambda x: x not in ['strc', 'attr', '{}'], region)
    conc = [[words] for segments in conc for words in segments.split()]
  else:
    conc = isplit(region, ['strc', 'attr'])
    conc = [[x.split('\t') for x in subconc] for subconc in conc]
    conc = [flatten(x) for x in conc]
    conc = filter(lambda x: x not in [['strc'], ['attr']], conc)
    conc = [filter(None, filter(lambda x: x != '{}', x)) for x in conc]

  # Fix UTF-8 mess.
  conc = [[x.decode('utf-8') for x in xs] for xs in conc]
  return conc


# Convert a raw query result to a flat format (not dependencies etc.).
def cow_raw_to_flat(raw_conc, attrs):
  return [ { 'match_offset' : r['match_offset'], 'match_length' : r['match_length'], 'meta' : r['meta'], 'line' : cow_region_to_conc(r['region'], attrs) } for r in raw_conc]
