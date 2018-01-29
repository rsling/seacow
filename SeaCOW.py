# -*- coding: utf-8 -*-

import manatee
import os
import random
import time
import sys
import re
from time import gmtime, strftime
import pybloom_live
from SeaCOWUtils import isplit, flatten, cow_region_to_conc

if not os.environ.get('MANATEE_REGISTRY'):
  os.environ['MANATEE_REGISTRY'] = '/var/lib/manatee/registry'

DEFAULT_CORPUS     = 'decow16a-nano'
DEFAULT_ATTRIBUTES = ['word', 'tag', 'lemma', 'depind', 'dephd', 'deprel']
DEFAULT_STRUCTURES = ['s', 'nx']
DEFAULT_REFERENCES = ['doc.url', 'doc.bdc', 'doc.tld', 'doc.id', 'div.bpc', 's.idx', 's.type']
DEFAULT_CONTAINER  = 's'

class QueryNotPrepared(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)


class Query:
  """SeaCOW query class"""

  def __init__(self):
    self.corpus        = DEFAULT_CORPUS
    self.attributes    = DEFAULT_ATTRIBUTES
    self.structures    = DEFAULT_STRUCTURES
    self.references    = DEFAULT_REFERENCES
    self.container     = DEFAULT_CONTAINER
    self.string        = None
    self.max_hits      = -1
    self.random_subset = -1
    self.context_left  = 0
    self.context_right = 0

    self.bloom         = None

    # Set this to a region processor.
    self.processor     = None

    # Properties of last query.
    self.querytime     = None
    self.hits          = 0
    self.duplicates    = 0
    self.elpased       = 0

  def set_deduplication(self, off = False):
    if off:
      self.bloom = None
    else:
      self.bloom = pybloom_live.ScalableBloomFilter(mode = pybloom_live.ScalableBloomFilter.LARGE_SET_GROWTH)

  def run(self):

    # Check whether query is prepared.
    if self.string is None or self.string is '':
      raise QueryNotPrepared('You must set the string property to a search string.')

    # Check whether processor of proper type
    if self.processor and not issubclass(type(self.processor), Processor):
      raise QueryNotPrepared('The processor class must inherit from SeaCOW.Processor.')

    # Allow the processor to engage in preparatory action/check whether everything is fine.
    if self.processor:
      self.processor.prepare(self)

    # Set up and run query.
    h_corpus     = manatee.Corpus(self.corpus)
    h_region     = manatee.CorpRegion(h_corpus, ','.join(self.attributes), ','.join(self.structures))
    h_cont       = h_corpus.get_struct(self.container)
    h_refs       = [h_corpus.get_attr(r) for r in self.references]
    start_time   = time.time()
    results      = h_corpus.eval_query(self.string)

    # Process results.
    counter  = 0
    dup_no   = 0

    while not results.end() and (self.max_hits < 0 or counter < self.max_hits):

      # Skip randomly if random subset desired.
      if self.random_subset > 0 and random.random() > self.random_subset:
        results.next()
        continue

      kwic_beg = results.peek_beg()                                  # Match begin.
      kwic_end = results.peek_end()                                  # Match end.
      cont_beg_num = h_cont.num_at_pos(kwic_beg)-self.context_left   # Container at match begin.
      cont_end_num = h_cont.num_at_pos(kwic_beg)+self.context_right  # Container at match end.

      # If hit not in desired region, drop.
      if cont_beg_num < 0 or cont_end_num < 0:
        results.next()
        continue

      cont_beg_pos = h_cont.beg(cont_beg_num)                   # Pos at container begin.
      cont_end_pos = h_cont.end(cont_end_num)                   # Pos at container end.

      # TODO RS Memory and time (likely malloc, CPU load actually *lower*) lost in next 2 lines!
      refs = [h_refs[i].pos2str(kwic_beg) for i in range(0, len(h_refs))]
      region = h_region.region(cont_beg_pos, cont_end_pos, '\t', '\t')

      # Deduping.
      if type(self.bloom) is pybloom_live.ScalableBloomFilter:
        dd_region = ''.join([region[i].strip().lower() for i in range(0, len(region), 1+len(self.attributes))])
        if {dd_region : 0} in self.bloom:
          dup_no += 1
          results.next()
          continue
        else:
          self.bloom.add({dd_region : 0})

      # Call the processor.
      if self.processor:
        self.processor.process(self, region, refs, kwic_beg - cont_beg_pos, kwic_end - kwic_beg)

      # Advance stream/loop.
      results.next()
      counter = counter + 1

    self.querytime     = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    self.hits          = counter
    self.duplicates    = dup_no
    self.elapsed       = time.time()-start_time

    # Allow the processor to finalise its job.
    if self.processor:
      self.processor.finalise(self)


class Processor(object):
  """SeaCOW processor class"""

  def __init__(self):
    raise Exception('You cannot use the Processor class directly. Implement an ancestor!')

  def prepare(self, query):
    print "You are calling a processor with unimplemented methods: " + str(type(self))

  def finalise(self, query):
    print "You are calling a processor with unimplemented methods: " + str(type(self))

  def process(self, query, region, meta, match_offset, match_length):
    print "You are calling a processor with unimplemented methods: " + str(type(self))


class ConcordanceWriter(Processor):
  """SeaCOW processor class for concordance writing"""

  def __init__(self):
    self.filename = None

  def prepare(self, query):
    self.handle         = open(self.filename, 'w') if self.filename else sys.stdout
    self.has_attributes = True if len(query.attributes) > 1 else False
    self.rex            = re.compile('^<.+>$')

    self.handle.write('# = BASIC =============================================================\n')
    self.handle.write('# QUERY:         %s\n' % query.string)
    self.handle.write('# CORPUS:        %s\n' % query.corpus)
    self.handle.write('# = CONFIG ============================================================\n')
    self.handle.write('# MAX_HITS:      %s\n' % query.max_hits)
    self.handle.write('# RANDOM_SUBSET: %s\n' % query.random_subset)
    self.handle.write('# ATTRIBUTES:    %s\n' % ','.join(query.attributes))
    self.handle.write('# STRUCTURES:    %s\n' % ','.join(query.structures))
    self.handle.write('# REFERENCES:    %s\n' % ','.join(query.references))
    self.handle.write('# CONTAINER:     %s\n' % query.container)
    self.handle.write('# CNT_LEFT:      %s\n' % query.context_left)
    self.handle.write('# CNT_RIGHT:     %s\n' % query.context_right)
    self.handle.write('# DEDUPING:      %s\n' % str(query.bloom is not None))
    self.handle.write('# = CONCORDANCE TSV ===================================================\n')

  def finalise(self, query):
    self.handle.write('# = STATS =============================================================\n')
    self.handle.write('# HITS:          %s\n' % query.hits)
    self.handle.write('# DUPLICATES:    %s\n' % query.duplicates)
    self.handle.write('# QUERY TIME:    %s\n' % query.querytime)
    self.handle.write('# ELAPSED:       %s s\n' % str(query.elapsed))
    self.handle.write('# =====================================================================\n')

    # Close file handle if writing to file.
    if self.handle is not sys.stdout:
      self.handle.close()

  def process(self, query, region, meta, match_offset, match_length):

    # Turn Mantee stuff into usable structure.
    line         = cow_region_to_conc(region, self.has_attributes)

    # Find true tokens via indices (not structs) for separating match from context.
    indices      = [i for i, s in enumerate(line) if not self.rex.match(s[0])]
    match_start  = indices[match_offset]
    match_end    = indices[match_offset + match_length - 1]
    match_length = match_end - match_start + 1

    # Write meta, left, match, right.
    self.handle.write('\t'.join(meta) + '\t')
    self.handle.write(' '.join(['|'.join(token) for token in line[:match_start]]) + '\t')
    self.handle.write(' '.join(['|'.join(token) for token in line[match_start:match_end+1]]) + '\t')
    self.handle.write(' '.join(['|'.join(token) for token in line[match_end+1:]]) + '\n')
