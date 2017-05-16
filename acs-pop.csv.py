from muck import *
from pithy.io import *
from pithy.csv_utils import *


seq_id = 3 # contains population count.

desired_col_names = {
  'STUSAB',
  'LOGRECNO',
  'B01003_001: TOTAL POPULATION for Total Population%Total',
}

def main():
  headers = load('acs-seq-headers.json')
  state_abbrs = load('state-abbrs.json')
  input_header = headers[seq_id]
  col_idx_names = [(i, n) for i, n in enumerate(input_header) if n in desired_col_names]
  out_header = [n for i, n in col_idx_names]

  for i, n in col_idx_names:
    if n == 'STUSAB': stusab_idx = i
    elif n == 'LOGRECNO': lrn_idx = i
    elif n == 'B01003_001: TOTAL POPULATION for Total Population%Total': pop_idx = i

  errSL('pop_idx:', pop_idx)

  def gen_state_rows(state):
    state_l = state.lower()
    path = f'Tracts_Block_Groups_Only/e20155{state_l}{seq_id:04}000.txt'
    errL(path)
    lrns = set()
    for row in load(path, ext='.csv', header=None):
      assert_eq(len(input_header), len(row))
      assert_eq(state_l, row[stusab_idx])
      assert_eq('000', row[3]) # chariter is always 0 for standard 5-year product.
      lrn = row[lrn_idx]
      assert lrn not in lrns
      lrns.add(lrn)
      row[stusab_idx] = row[stusab_idx].upper()
      yield [row[i] for i, n in col_idx_names]

  def gen_rows():
    for state in state_abbrs:
      if state in ('GU', 'VI'): continue # no geography file provided.
      yield from gen_state_rows(state)

  out_csv(header=out_header, rows=gen_rows())


#STUSAB,LOGRECNO,COUNTY,TRACT,BLKGRP,GEOID,NAME,ALAND,AWATER,INTPTLAT,INTPTLONG
#AL,0001760,001,020100,,01001020100,"Census Tract 201, Autauga County, Alabama",9809938,36312,32.4819591,-86.4913377

#'FILEID', 'FILETYPE', 'STUSAB', 'CHARITER', 'SEQUENCE', 'LOGRECNO', '
#ACSSF,2015e5,al,000,0001,0001760,251,99

main()
