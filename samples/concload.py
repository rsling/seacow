# -*- coding: utf-8 -*-

from SeaCOW import Query, ConcordanceLoader
import json # Just for pretty-printing.

# See sample.py for annotations of these attributes.
q = Query()
q.corpus          = 'decow16a-nano'
q.string          = '[word="Hausfrau"]'
q.max_hits        = 10
q.attributes      = ['word', 'tag']
q.structures      = ['s']
q.references      = ['doc.url', 'doc.bdc', 'doc.tld', 'doc.id', 'div.bpc', 's.idx', 's.type']
q.container       = 's'
q.set_deduplication()

# The concordance loader has just one settable attribute.
p                 = ConcordanceLoader()
p.full_structure  = True                 # Convert token attributes to dicts as well, otherwise |-separated.
q.processor       = p
q.run()

# Now you have a nice structured Python object in p.concordance.

# You don't need json. It's just a convenient way to display the result sturctures for this demo.
print json.dumps(p.concordance[0:2], sort_keys=False, indent=2)

