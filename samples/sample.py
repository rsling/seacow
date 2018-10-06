# -*- coding: utf-8 -*-

from SeaCOW import Query, ConcordanceWriter, DependencyBuilder

# Create a Query object and set whatever needs to be set.
q = Query()
q.corpus          = 'decow16a-nano'         # Lower-case name of the corpusto use.
q.string          = '[word="Hausfrau"]'     # A normal CQL string as used in NoSketchEngine.
q.max_hits        = 10                      # Maximal number of hits to return. Use when testing queries!
q.attributes      = ['word']                # Attributes (of tokens) to export from corpus.
q.structures      = ['s']                   # Structure markup to export from corpus.
q.references      = ['doc.url', 'doc.bdc', 'doc.tld', 'doc.id', 'div.bpc', 's.idx', 's.type']
                                            # Which reference attributes (of structures) to export.
q.container       = 's'                     # Which container strutcure should be exported?

# This enables an efficient duplicate remover using a scaling Bloom filter.
q.set_deduplication()

# Create a Processor object and attach it to the Query object.
# The ConcordanceWriter processor just writes a nice CSV file
# containing your concordance, incl. all meta data you need
# as comments at the top and bottom of the table.
p                 = ConcordanceWriter() # Create a processor object of apporpriate type.
p.filename        = 'hausfrau.csv'      # File name for output data. Directories MUST EXIST!
q.processor       = p                   # Attach the processor to the query.
q.run()                                 # Run the query.

