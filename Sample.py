# -*- coding: utf-8 -*-

from SeaCOW import Query, ConcordanceWriter, DependencyBuilder

# Create a Query object and set whatever needs to be set.
q = Query()

q.set_deduplication()

q.string          = '[word="Hausfrau"]'
q.max_hits        = 1
q.attributes      = ['word']
q.structures      = ['s']

# Create a Processor object and attach it to the Query object.
p                 = ConcordanceWriter()
p.filename        = 'data/chuzpe.csv'
q.processor       = p

# Run the actual query.
q.run()

# You can then even attach a differen Processor and run the query again.
q.attributes      = ['word', 'depind', 'dephd', 'deprel']
p                 = DependencyBuilder()
p.column_token    = 0
p.column_index    = 1
p.column_head     = 2
p.column_relation = 3
q.processor       = p

q.run()
