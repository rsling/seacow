# -*- coding: utf-8 -*-

from SeaCOW import Query, ConcordanceWriter, DependencyBuilder

# FIRST QUERY.

# Create a Query object and set whatever needs to be set.
q = Query()
q.corpus          = 'decow16a-nano'
q.string          = '[word="Hausfrau"]'
q.max_hits        = 10
q.attributes      = ['word']
q.structures      = ['s']
q.references      = ['doc.url', 'doc.bdc', 'doc.tld', 'doc.id', 'div.bpc', 's.idx', 's.type']
q.container       = 's'

# This enables an efficient duplicate remover using a scaling Bloom filter.
q.set_deduplication()

# Create a Processor object and attach it to the Query object.
# The ConcordanceWriter processor just writes a nice CSV file
# containing your concordance, incl. all meta data you need
# as comments at the top and bottom of the table.
p                 = ConcordanceWriter()
p.filename        = 'data/hausfrau.csv'
q.processor       = p

# Run the actual query.
q.run()

# SECOND QUERY.

# You can then even attach a differen Processor and run the query again.
# The dependency builder reconstructs (and outputs) dependency trees.
# If you want to filter structures, create a class which inherits from
# DependencyBuilder and override the filtre() method (NO TYPO there).
q.attributes      = ['word', 'depind', 'dephd', 'deprel', 'tag', 'lemma']
p                 = DependencyBuilder()
p.column_token    = 0
p.column_index    = 1
p.column_head     = 2
p.column_relation = 3
p.attribs         = [4,5]
p.fileprefix      = 'data/hausfrau'
p.savejson        = True
p.saveimage       = 'png'
p.imagemetaid1    = 3
p.imagemetaid2    = 5
p.printtrees      = True
q.processor       = p

q.run()
