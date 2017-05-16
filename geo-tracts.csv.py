from muck import *
from pithy.io import *
from pithy.csv_utils import *


desired_col_names = {
  'STUSAB', # US state abbreviation.
  'LOGRECNO', # logical record number.
  'COUNTY', # FIPS code?
  'TRACT', # census tract.
  'BLKGRP', # block group.
  'GEOID',
  'NAME', # description text.
}

desired_gaz_fields = [
  'ALAND',
  'AWATER',
  'INTPTLAT',
  'INTPTLONG',
]


geoid_prefix = '14000US'


def main():
  input_header = load('geo-header.json')
  state_abbrs = load('state-abbrs.json')
  col_idx_names = [(i, n) for (i, (n, desc)) in enumerate(input_header) if n in desired_col_names]
  errSL('geo column indexes:', col_idx_names)
  out_header = [n for (i, n) in col_idx_names] + desired_gaz_fields
  errSL('output header:', out_header)

  for i, n in col_idx_names:
    if n == 'TRACT': tract_idx = i
    elif n == 'BLKGRP': blockgroup_idx = i
    elif n == 'GEOID': geoid_idx = i

  gaz = parse_gaz()

  def gen_rows():
    for state in state_abbrs:
      if state in ('GU', 'VI'): continue # no geography file provided.
      errL(state)
      for row in load(f'2015_ACS_Geography_Files/g20155{state.lower()}.csv', encoding='cp1252'):
        if row[tract_idx] == '': continue # not a tract or blockgroup.
        if row[blockgroup_idx] != '': continue # skip blockgroups for now, because there is no corresponding gaz data.
        geoid = row[geoid_idx]
        assert geoid.startswith(geoid_prefix), geoid
        geoid = geoid[len(geoid_prefix):] # trim prefix to match standard geoids in gaz and other datasets.
        row[geoid_idx] = geoid
        g = gaz[geoid]
        r = [row[i] for (i, n) in col_idx_names] + [g[k] for k in desired_gaz_fields]
        assert len(r) == len(out_header)
        yield r

  out_csv(header=out_header, rows=gen_rows())


def parse_gaz():
  '''
  Use the gazetteer dataset to get location points for the census tracts.
  This is much easier than using TIGER line data or other geodatabase datasets,
  but is only available for tract level, not block groups.
  The file appears to be tab-separated, but with extra spaces, so we just parse it manually.
  '''
  header = ['USPS', 'GEOID', 'ALAND', 'AWATER', 'ALAND_SQMI', 'AWATER_SQMI', 'INTPTLAT', 'INTPTLONG']
  gaz = {}
  first = True
  for line in load('2015_Gaz_tracts_national.txt'):
    row = line.split()
    if first: # gaz header.
      first = False
      assert_eq(row, header)
      continue
    assert_eq(len(row), len(header))
    r = {n: v for (n, v) in zip(header, row)}
    geoid = r['GEOID']
    assert geoid not in gaz, r
    gaz[geoid] = r
  return gaz

main()
