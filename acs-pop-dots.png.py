from muck import *
from math import log2, sqrt
from typing import NamedTuple
from pithy.io import *
from pithy.immutable import Immutable
from pithy.iterable import min_max, count_by_pred

from PIL import Image, ImageDraw


excluded_states = {
  'AK',
  'HI',
  'GU',
  'PR',
  'VI',
}


class Dot(NamedTuple):
  pop: float
  area: float
  lat: float
  lon: float

  @property
  def pop_density(self) -> float:
    if self.pop == 0: return 0
    return self.pop / self.area


def main():
  'since both datasets come sorted by LOGRECNO, we can simply parse them lazily and zip to join them.'
  dots = []
  for g, p in err_progress(zip(parse_geo(), parse_pop())):
    assert g.STUSAB == p.STUSAB, (g, p)
    assert g.LOGRECNO == p.LOGRECNO
    if g.ALAND == '':
      assert g.BLKGRP != '', g # skip blockgroups, which do not yet have geo data.
      continue
    if g.STUSAB in excluded_states: continue
    dots.append(mk_dot(g, p))
  render(dots)


def parse_geo():
  geo_header = ['STUSAB', 'LOGRECNO', 'COUNTY', 'TRACT', 'BLKGRP', 'GEOID', 'NAME', 'ALAND', 'AWATER', 'INTPTLAT', 'INTPTLONG']
  for row in load('acs-geo.csv', header=geo_header):
    yield Immutable(*zip(geo_header, row))


def parse_pop():
  pop_header = ['STUSAB', 'LOGRECNO', 'B01003_001: TOTAL POPULATION for Total Population%Total']
  fields = pop_header[:2] + ['POPULATION']
  for row in load('acs-pop.csv', header=pop_header):
    yield Immutable(*zip(fields, row))


def mk_dot(g, p):
  try:
    return Dot(
      pop=float(p.POPULATION),
      area=float(g.ALAND),
      lat=float(g.INTPTLAT),
      lon=float(g.INTPTLONG))
  except Exception as e:
    errSL('g:', g)
    errSL('p:', p)
    errSL('e:', type(e), e)
    raise


def render(dots):
  errSL('dots:', len(dots))
  pop_min, pop_max = min_max(d.pop for d in dots)
  area_min, area_max = min_max(d.area for d in dots)
  dens_min, dens_max = min_max(filter(None, (d.pop_density for d in dots)))
  errL(f'pop: {pop_min} ... {pop_max}')
  errL(f'area: {area_min} ... {area_max}')
  errL(f'density (excluding zeros): {dens_min} ... {dens_max}; min sq m per person: {1/dens_max}')

  zero_pops   = count_by_pred(dots, lambda d: d.pop == 0)
  zero_areas  = count_by_pred(dots, lambda d: d.area == 0)
  errL(f'zero pop: {zero_pops}; zero area: {zero_areas}')

  dens_lin_scale = 2 / dens_min # want minimum observed density to have a log2 value of 1.
  dens_log_scale = 1 / log2(dens_max * dens_lin_scale) # want max observed density to be 1 on the log2 scale.

  x_min = min(d.lon for d in dots)
  x_max = max(d.lon for d in dots)
  y_min = min(d.lat for d in dots)
  y_max = max(d.lat for d in dots)
  w = x_max - x_min
  h = y_max - y_min
  ar = w / h
  errL(f'w = {w}; {x_min} ... {x_max}')
  errL(f'h = {h}; {y_min} ... {y_max}')
  errL(f'ar: {ar}')

  w_px = 1024 * 4
  h_px = int(w_px / ar)

  margin = 1/16
  xm = w * margin
  ym = h * margin
  xo = x_min - xm
  yo = y_min - ym
  xs = w_px / (x_max + xm - xo)
  ys = h_px / (y_max + ym - yo)

  def coord(dot):
    return (dot.lon - xo) * xs, h_px - (dot.lat - yo) * ys

  def box(dot):
    x, y = coord(dot)
    r = sqrt(dot.area / area_max) * 12
    return (x - r, y - r, x + r, y + r)

  def color(dot):
    d = dot.pop_density
    if d == 0:
      i = 0
    else:
      v = log2(d * dens_lin_scale) * dens_log_scale
      i = int(round(255 * v))
    return (0, i, 0)

  img = Image.new(mode='RGB', size=(w_px, h_px))
  draw = ImageDraw.Draw(img)
  for dot in err_progress(dots):
    draw.ellipse(box(dot), fill=color(dot), outline=None)
  img.save(stdout.buffer, 'PNG', dpi=(220, 220))


main()
