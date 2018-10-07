# -*- coding: utf-8 -*-

from SeaCOW import Query, ConcordanceDumper

q = Query()
q.corpus          = 'decow16a-nano'
q.string          = '[word="Hausfrau"]'
q.max_hits        = 10
q.attributes      = ['word']
q.structures      = ['s']
q.references      = ['doc.url', 'doc.bdc', 'doc.tld', 'doc.id', 'div.bpc', 's.idx', 's.type']
q.container       = 's'
q.set_deduplication()

p                 = ConcordanceDumper()
p.filename        = 'hausfrau.csv'
q.processor       = p
q.run()

