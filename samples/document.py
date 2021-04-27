# -*- coding: utf-8 -*-

import random
from SeaCOW import Query, ConcordanceWriter, DependencyBuilder

random.seed(2914)

q = Query()
q.corpus          = 'precox20lda25'
q.string          = '<doc id="[0-9a-f].+">'
q.random_subset   =  0.09
q.attributes      = ['word']
q.structures      = ['s.idx', 'div.bpc', 'doc.bdc', 'doc.url', 'doc.id', 'doc.pregister', 'doc.pregbrob']
q.references      = ['doc.url', 'doc.id']
q.container       = 'doc'

p                 = ConcordanceWriter()
p.filename        = 'sample.csv'
q.processor       = p
q.run()

