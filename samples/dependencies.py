# -*- coding: utf-8 -*-

from SeaCOW import Query, ConcordanceWriter, DependencyBuilder

# Create a Query object and set whatever needs to be set.
q = Query()
q.corpus          = 'decow16b'         # Lower-case name of the corpusto use.
q.string          = '[word="Motorsäge"]'    # A normal CQL string as used in NoSketchEngine.
q.max_hits        = 10                      # Maximal number of hits to return. Use when testing queries!
q.structures      = ['s']                   # Structure markup to export from corpus.
q.references      = ['doc.url', 'doc.bdc', 'doc.tld', 'doc.id', 'div.bpc', 's.idx', 's.type']
                                            # Which reference attributes (of structures) to export.
q.container       = 's'                     # Which container strutcure should be exported?
q.set_deduplication()                       # Use deduplication.


# The dependency attributes are needed for DependencyBuilder() to work.
q.attributes      = ['word', 'depind', 'dephd', 'deprel', 'tag', 'lemma']


# The dependency builder reconstructs (and outputs) dependency trees.
# If you want to filter structures, create a class which inherits from
# DependencyBuilder and override the filtre() method (NO TYPO there).
p                 = DependencyBuilder()

# The following five are 0-based indeces into q.attributes as defined above.
p.column_token    = 0                    # Which column contains the token?
p.column_index    = 1                    # Which column contains the dependency index?
p.column_head     = 2                    # Which column contains the dependency head index?
p.column_relation = 3                    # Which column contains the dependency relation?
p.attribs         = [4,5]                # A list of additional attributes to copy to the tree nodes.

# Other attributes of DependencyBuilder().
p.fileprefix      = 'output/motorsaege'  # File name prefix for output data. Directories MUST EXIST!
p.savejson        = True                 # Whether a JSON file should be saved.
p.saveimage       = 'png'                # Whether ONE PNG FILE PER FOUND TREE should be written.
                                         # None: Don't write anything. 'png' or 'dot': write files of respective type.
p.imagemetaid1    = 3                    # Attribute which serves as first file name component for graphics files.
p.imagemetaid2    = 5                    # Attribute which serves as second file name component for graphics files. (OPTIONAL)
p.printtrees      = False                # Print all trees using ASCII to stdout?

q.processor       = p                    # Attach the processor to the query.
q.run()                                  # Run the query.
