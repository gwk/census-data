import re
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
  input_header = headers[seq_id]
  col_idx_names = [(i, n) for i, n in enumerate(input_header) if n in desired_col_names]
  out_header = [n for i, n in col_idx_names]

  for i, n in col_idx_names:
    if n == 'STUSAB': stusab_idx = i
    elif n == 'LOGRECNO': lrn_idx = i

  def gen_state_rows(f, state_lower):
    errSL(state_lower, '-', f)
    lrns = set() # verify that all logical record numbers are unique within a state.
    for row in load(f, ext='.csv', header=None):
      assert_eq(len(input_header), len(row))
      assert_eq(state_lower, row[stusab_idx])
      assert_eq('000', row[3]) # chariter is always 0 for standard 5-year product.
      lrn = row[lrn_idx]
      assert lrn not in lrns
      lrns.add(lrn)
      row[stusab_idx] = row[stusab_idx].upper()
      yield [row[i] for i, n in col_idx_names]

  def gen_rows():
    archive = load('data/Tracts_Block_Groups_Only.tar.gz')
    for f in archive:
      m = re.match(r'group2/e20155(\w{2})(\d{4})(\d{3}).txt', f.name)
      if not m: continue # only interested in the estimate files.
      state_lower, seq, chariter = m.groups()
      assert_eq('000', chariter) # always 0 for standard 5-year product.
      if int(seq) != seq_id: continue # for now only interested in one column.
      if state_lower in ('gu', 'vi'): continue # no geography file provided.
      yield from gen_state_rows(f, state_lower)

  out_csv(header=out_header, rows=sorted(gen_rows(), key=lambda r: r[:2])) # sort everything by state and record number.


main()
