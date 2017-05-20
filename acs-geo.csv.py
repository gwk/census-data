import re
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


geoid_tract_prefix      = '14000US'
geoid_blockgroup_prefix = '15000US'

def main():
  input_header = load('acs-geo-header.json')
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
    for f in load('data/2015_ACS_Geography_Files.zip'):
      if not f.name.endswith('.csv'): continue # ignore the .txt files, which present the same info in a less helpful format.
      errL(f)
      for row in load(f, encoding='cp1252'):
        if row[tract_idx] == '': continue # not a tract or blockgroup.
        is_tract = (row[blockgroup_idx] == '')
        geoid_prefix = (geoid_tract_prefix if is_tract else geoid_blockgroup_prefix)
        geoid = row[geoid_idx]
        assert geoid.startswith(geoid_prefix), geoid
        geoid = geoid[len(geoid_prefix):] # trim prefix to match standard geoids in gaz and other datasets.
        row[geoid_idx] = geoid
        sr = [row[i] for (i, n) in col_idx_names]
        if is_tract: # tract.
          g = gaz[geoid]
          gr = [g[k] for k in desired_gaz_fields]
        else: # blockgroup; no corresponding gaz data.
          gr = ['' for k in desired_gaz_fields]
        r = sr + gr
        assert len(r) == len(out_header)
        yield r

  out_csv(header=out_header, rows=sorted(gen_rows(), key=lambda r: r[:2]))


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
  for line in load('data/2015_Gaz_tracts_national.zip', single_name='2015_Gaz_tracts_national.txt'):
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
