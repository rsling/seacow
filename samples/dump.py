# -*- coding: utf-8 -*-

# This dumps a very raw concordance format.
# It's very efficient, though.
# See samply.py for options.

from SeaCOW import Query, ConcordanceDumper

q = Query()
q.corpus          = 'encow16a-nano'
q.string          = '[tag="N."][word="attention"]'
q.max_hits        = -1
q.attributes      = ['word']
q.structures      = ['s']
q.references      = ['doc.url', 'doc.id', 's.idx']
q.container       = 's'
q.set_deduplication()

p                 = ConcordanceDumper()
p.filename        = 'dump.txt'
q.processor       = p
q.run()
