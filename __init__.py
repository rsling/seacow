# -*- coding: utf-8 -*-

"""Making queries in COW using Manatee."""

__version__ = "0.2"
__author__ = "Roland Schäfer"
__author_email__ = "roland.schaefer@fu-berlin.de"
__description__ = """Making queries in COW using Manatee."""
__url__ = "https://github.com/rsling/seacow"

from SeaCOW import Query, Nonprocessor, ConcordanceLoader, ConcordanceWriter, ConcordanceDumper, DependencyBuilder, Processor, cow_region_to_conc, cow_rough_region_to_conc
