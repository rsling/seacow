# -*- coding: utf-8 -*-

import manatee
import os
import random
import time
import sys
import re
from time import gmtime, strftime
import pybloom_live
from anytree import Node, RenderTree
from anytree.exporter import DotExporter, JsonExporter
from SeaCOWUtils import isplit, flatten, cow_region_to_conc, cow_rough_region_to_conc



if not os.environ.get('MANATEE_REGISTRY'):
  os.environ['MANATEE_REGISTRY'] = '/var/lib/manatee/registry'



class QueryError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)




class ProcessorError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)





class Query:
  """SeaCOW query class"""

  def __init__(self):
    self.corpus        = None
    self.subcorpus     = None
    self.attributes    = None
    self.structures    = None
    self.references    = None
    self.container     = None
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
    if self.corpus is None:
      raise QueryError('You must specify the corpus to do a search.')
    if self.attributes is None:
      raise QueryError('You must specify at least one attribute to do a search.')
    if self.structures is None:
      raise QueryError('You must specify at least one structure to do a search.')
    if self.references is None:
      raise QueryError('You must specify at least one reference to do a search.')
    if self.container  is None and not issubclass(type(self.processor), Nonprocessor):
      raise QueryError('You must specify the container to do a search.')
    if self.string is None or self.string is '':
      raise QueryError('You must set the string property to a search string.')

    # Check whether processor of proper type
    if self.processor and not issubclass(type(self.processor), Processor):
      raise QueryError('The processor class must inherit from SeaCOW.Processor.')

    # Emit heuristic warning that container might end up being to small.
    # This warns about the behviour reported 2020 by EP.
    q_pattern = r'.* within *<' + self.container + r'(| [^>]+)/>.*'
    q_string = r'within <' + self.container + r'/>'
    if not re.match(q_pattern, self.string):
      print("WARNING! Your query should probably end in '" + q_string + "' or your match might exceed the exported container.")
      if self.context_left == 0 or self.context_right == 0:
        print(" ... especially because at least one of your contexts is 0!")
      print(" ... Watch out for 'Index anomaly' warnings.")
      print


    # Allow the processor to engage in preparatory action/check whether everything is fine.
    if self.processor:
      self.processor.prepare(self)

    # Set up and run query.
    h_corpus      = manatee.Corpus(self.corpus)
    if self.subcorpus is not None:
        # If subcorpus name is given (instead of path), figure out full path to subcorpus .subc file.
        if not "/" in self.subcorpus:
            self.subcorpus = h_corpus.get_conf("PATH") + "subcorp/" + re.sub("\.subc$", "", self.subcorpus.strip(" /")) + ".subc"
        if os.path.exists(self.subcorpus):
            h_corpus = manatee.SubCorpus (h_corpus, self.subcorpus)
        else:
            raise QueryError('The requested subcorpus cannot be found.')

    if not issubclass(type(self.processor), Nonprocessor):
      h_region      = manatee.CorpRegion(h_corpus, ','.join(self.attributes), ','.join(self.structures))
      h_cont        = h_corpus.get_struct(self.container)
      h_refs        = [h_corpus.get_attr(r) for r in self.references]

    start_time    = time.time()
    results       = h_corpus.eval_query(self.string)

    # Process results.
    counter  = 0
    dup_no   = 0

    # In case class is "Noprocessor", we do not process the stream.
    if issubclass(type(self.processor), Nonprocessor):

      # Store the hit count as reported.
      self.hits = results.count_rest()
    else:
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

      # After loop but inside "if not Nonprocessor", set hit count.
      self.hits          = counter

    self.querytime     = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    self.duplicates    = dup_no
    self.elapsed       = time.time()-start_time

    # Allow the processor to finalise its job.
    if self.processor:
      self.processor.finalise(self)





class Processor(object):
  """SeaCOW processor class"""

  def __init__(self):
    raise Exception('You cannot use the Processor class directly. Please implement a descendant!')

  def prepare(self, query):
    print ( "You are calling a Processor with an unimplemented prepare() method: " + str(type(self)) )

  def finalise(self, query):
    print ( "You are calling a Processor with an unimplemented finalise() method: " + str(type(self)) )

  def process(self, query, region, meta, match_offset, match_length):
    print ( "You are calling a Processor with an unimplemented process() method: " + str(type(self)) )



class Nonprocessor(Processor):
  """SeaCOW processor class which does not process the stream"""

  def __init__(self):
    pass

  def prepare(self, query):
    pass

  def finalise(self, query):
    pass

  def process(self, query, region, meta, match_offset, match_length):
    pass



class ConcordanceLoader(Processor):
  """SeaCOW processor class for loading a concordance into a Python object"""

  def __init__(self):
    self.filename = None
    self.full_structure = False

  def prepare(self, query):
    self.has_attributes = True if len(query.attributes) > 1 else False
    self.rex            = re.compile('^<.+>$')
    self.concordance    = list()

  def finalise(self, query):

    # Nothing to do.
    pass


  def process(self, query, region, meta, match_offset, match_length):

    # Turn Mantee stuff into usable structure.
    line         = cow_region_to_conc(region, self.has_attributes)

    # Find true tokens via indices (not structs) for separating match from context.
    indices      = [i for i, s in enumerate(line) if not self.rex.match(s[0])]
    match_start  = indices[match_offset]

    # If someone does not search within <x/> but exports just x,
    # part of the match might be cut off. This skips the concordance line
    # in those situations. Prevents crashes reported 2020 by EP.
    if match_offset >= len(indices) or match_offset + match_length - 1 >= len(indices):
      print("Index anomaly! You just lost a concordance line.")
      print("Are you querying matches that might exceed the exported container?")
      print
      return

    match_end    = indices[match_offset + match_length - 1]
    match_length = match_end - match_start + 1

    # Build concordance line and add to output list.
    if self.full_structure:
      concline = {
        "meta"  : dict(zip(query.references, meta)),
        "left"  : [str(token[0]) if re.match(r'<', token[0], re.UNICODE) else dict(zip(query.attributes, token)) for token in line[:match_start]],
        "match" : [str(token[0]) if re.match(r'<', token[0], re.UNICODE) else dict(zip(query.attributes, token)) for token in line[match_start:match_end+1]],
        "right" : [str(token[0]) if re.match(r'<', token[0], re.UNICODE) else dict(zip(query.attributes, token)) for token in line[match_end+1:]]
        }
    else:
      concline = {
        "meta"  : dict(zip(query.references, meta)),
        "left"  : ['|'.join(token) for token in line[:match_start]],
        "match" : ['|'.join(token) for token in line[match_start:match_end+1]],
        "right" : ['|'.join(token) for token in line[match_end+1:]]
        }
    self.concordance.append(concline)




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
    self.handle.write('# SUBCORPUS:     %s\n' % query.subcorpus)
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
    self.handle.write('\t'.join(query.references + ['left.context', 'match', 'right.context']) + '\n')

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
    for i in line:
        print(i)

    # Find true tokens via indices (not structs) for separating match from context.
    indices      = [i for i, s in enumerate(line) if not self.rex.match(s[0])]
    match_start  = indices[match_offset]
    match_end    = indices[match_offset + match_length - 1]
    match_length = match_end - match_start + 1

    # Write meta, left, match, right.
    self.handle.write('\t'.join(meta) + '\t')
    self.handle.write((' '.join(['|'.join(token) for token in line[:match_start]]) + '\t').encode('utf-8'))
    self.handle.write((' '.join(['|'.join(token) for token in line[match_start:match_end+1]]) + '\t').encode('utf-8'))
    self.handle.write((' '.join(['|'.join(token) for token in line[match_end+1:]]) + '\n').encode('utf-8'))



class ConcordanceDumper(Processor):
  """SeaCOW processor class for concordance dumping (corpquery-style)"""

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
    self.handle.write('\t'.join(query.references + ['left.context', 'match', 'right.context']) + '\n')

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

    # Turn Mantee stuff into unstructured list.
    line         = cow_rough_region_to_conc(region)

    # Write meta and all the stuff.
    self.handle.write('\t'.join(meta + [str(match_offset), str(match_length)]) + '\t' + ' '.join(line) + '\n')






def edgeattrfunc(node, child):
  return 'label="%s"' % (child.relation)

def nodenamefunc(node):
  return '%s(%s)' % (make_token_safe(node.token), node.linear)

def make_token_safe(token):
  return(token.replace('"', 'DQUOTES').replace("'", 'SQUOTES'))

class DependencyBuilder(Processor):
  """SeaCOW processor class for concordance writing"""

  def __init__(self):
    self.column_index    = None
    self.column_head     = None
    self.column_relation = None
    self.column_token    = None
    self.fileprefix      = None
    self.savejson        = False
    self.saveimage       = None   # others: 'png' or 'dot'
    self.printtrees      = False
    self.imagemetaid1    = None
    self.imagemetaid2    = None

  def prepare(self, query):

    if self.saveimage and not self.imagemetaid1:
      raise ProcessorError('You cannot save to image files without setting at least imagemetaid1.')

    if not (self.column_token, self.column_index and self.column_head and self.column_relation):
      raise ProcessorError('You have to set the column indices for the dependency information.')

    self.has_attributes = True if len(query.attributes) > 1 else False
    self.rex            = re.compile('^<.+>$')

    if self.savejson:
      self.exporter = JsonExporter(indent = 2, sort_keys = False)
      self.writer = open(self.fileprefix + '.json', 'w')

  def finalise(self, query):
    return True

    if self.savejson:
      self.writer.close()


  def filtre(self, tree, line):
    return True

  def process(self, query, region, meta, match_offset, match_length):

    # Turn Mantee stuff into usable structure.
    line         = cow_region_to_conc(region, self.has_attributes)

    # Find true tokens via indices (not structs) for separating match from context.
    # Turn everything into nodes already - to be linked into tree in next step.
    indices      = [i for i, s in enumerate(line) if not self.rex.match(s[0])]
    nodes        = [Node("0", token = "TOP", relation = "", head = "", linear = 0, meta = dict(zip(query.references, meta))),] + \
                     [Node(make_token_safe(line[x][self.column_index]),
                     token    = line[x][self.column_token],
                     relation = line[x][self.column_relation],
                     head     = line[x][self.column_head],
                     linear   = int(line[x][self.column_index]),
                     **dict(zip([query.attributes[a] for a in self.attribs], [line[x][a] for a in self.attribs])) ) for x in indices]

    # Build tree from top.
    for n in nodes[1:]:
      n.parent = next((x for x in nodes if x.name == n.head), None)

    # If a descendant implements the filter, certain structures can be
    # discarded.
    if not self.filtre(nodes, line):
      return

    # Export as desired. Three independent formats.
    if self.printtrees:
      for pre, _, node in RenderTree(nodes[0]):
        print("%s%s (%s)" % (pre, node.token, node.name))

    if self.savejson:
      self.exporter.write(nodes[0], self.writer)

    if self.saveimage:
      fnam = self.fileprefix + '_' + meta[self.imagemetaid1]
      if self.imagemetaid2:
        fnam = fnam + '_' + meta[self.imagemetaid2]
      if self.saveimage is 'dot':
        DotExporter(nodes[0]).to_dotfile(fnam + '.dot')
      elif self.saveimage is 'png':
        DotExporter(nodes[0], edgeattrfunc = edgeattrfunc, nodenamefunc = nodenamefunc).to_picture(fnam + '.png')


