# -*- coding: utf-8 -*-

from SeaCOW import Query, Nonprocessor

# Create a Query object and set whatever needs to be set.
q = Query()
q.corpus          = 'decow16a-nano'         # Lower-case name of the corpusto use.
q.string          = '[word="Chuzpe"]'       # A normal CQL string as used in NoSketchEngine.
q.max_hits        = -1                      # Maximal number of hits to return. Ignored for Nonprocessor.
q.attributes      = []                      # For counting, you don't need word attributes.
q.structures      = []                      # ... you don't need structural attributes.
q.references      = []                      # ... you don't need reference attrs.
q.container       = None                    # Which container strutcure should be used? None is OK
                                            # only if class is Nonprocessor.

# Using the deduplicator would NOT change the outcome. Switch off.
q.set_deduplication(off = True)

# Create a Processor object and attach it to the Query object.
# The Nonprocessor processor does nothing. You can work with the results
# yourself in the finalise method or just get the hits value from the
# query object. It is the concordance as seported by Manatee.
p                 = Nonprocessor()  # Create a processor object of apporpriate type.
q.processor       = p               # Attach the processor to the query.
q.run()                             # Run the query.

print('Query was: %s' % (q.string))
print('Corpus used: %s' % (q.corpus))
print('Query returned %d hits.' % (q.hits))
