# -*- coding: utf-8 -*-

from SeaCOW import Query, ConcordanceWriter

# Create a Query object and set whatever needs to be set.
q = Query()

q.set_deduplication()

q.string     = '[word="Chuzpe"]'
q.max_hits   = 1
q.attributes = ['word']
q.structures = ['s']

# Create a Processor object and attach it to the Query object.
p            = ConcordanceWriter()
p.filename   = 'chuzpe2.csv'
q.processor  = p

# Run the actual query.
q.run()

