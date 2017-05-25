from muck import *
from pithy.io import *
from pithy.immutable import Immutable
from pithy.csv_utils import out_csv

from headers import *


def main():
  out_csv(header=geo_pop_header, rows=out_rows())


def out_rows():
  'since both datasets come sorted by LOGRECNO, we can simply parse them lazily and zip to join them.'
  dots = []
  for gr, pr in err_progress(zip(load('acs-geo.csv', header=geo_header), load('acs-pop.csv', header=pop_header))):
    g = Immutable(*zip(geo_header, gr))
    p = Immutable(*zip(pop_header, pr))
    assert g.STUSAB == p.STUSAB, (g, p)
    assert g.LOGRECNO == p.LOGRECNO
    if g.ALAND == '':
      assert g.BLKGRP != '', g # skip blockgroups, which do not yet have geo data.
      continue
    yield gr + pr[2:]


main()
