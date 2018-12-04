# -*- coding: utf-8 -*-

# This dumps a very raw concordance format.
# It's very efficient, though.
# See samply.py for options.

from SeaCOW import Query, ConcordanceDumper

q = Query()
q.corpus          = 'decow16a-nano'
q.string          = '[word="Chuzpe"]'
q.max_hits        = 10
q.attributes      = ['word']
q.structures      = ['s']
q.references      = ['doc.url', 'doc.id', 's.idx']
q.container       = 's'
q.set_deduplication()

p                 = ConcordanceDumper()
p.filename        = 'chuzpe.csv'
q.processor       = p
q.run()
