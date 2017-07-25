"""Implementation of TA records.

To this day, only records TA 836 and 890 are implemented.
There are no plans to support other types of records.
"""
from dta.records.record836 import DTARecord836
from dta.records.record890 import DTARecord890

__all__ = ['DTARecord836', 'DTARecord890']
