# -*- coding: utf-8 -*-

from SeaCOW import Query, ConcordanceWriter, DependencyBuilder
from iterated import IterativelyFiltredDependencyBuilder

# FIRST QUERY.

# Create a Query object and set whatever needs to be set.
q = Query()
q.corpus          = 'encow16a-nano'
q.string          = '[word="give" & tag="VB[ZPD]"]'
q.max_hits        = 100
q.attributes      = ['word', 'depind', 'dephd', 'deprel', 'tag', 'lemma']
q.structures      = ['s']
q.references      = ['doc.url', 'doc.bdc', 'doc.tld', 'doc.id', 'div.bpc', 's.idx', 's.type']
q.container       = 's'

# This enables an efficient duplicate remover using a scaling Bloom filter.
q.set_deduplication()


p                 = IterativelyFiltredDependencyBuilder()
p.column_token    = 0
p.column_index    = 1
p.column_head     = 2
p.column_relation = 3
p.attribs         = [4,5]
p.fileprefix      = 'give_iterated'
p.savejson        = True
p.saveimage       = 'png'
p.imagemetaid1    = 3
p.imagemetaid2    = 5
p.printtrees      = False
q.processor       = p

q.run()
