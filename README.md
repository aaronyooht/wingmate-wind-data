# wingmate-wind-data

Hourly-ish (every 6h, matching GFS cycles) global 10m wind grid (U/V components,
1° resolution) converted from NOAA GFS into the JSON format
[leaflet-velocity](https://github.com/onaci/leaflet-velocity) expects.

Built for the [WingMate](https://github.com/aaronyooht) crew app's wind
particle overlay — kept as its own lightweight repo since the WINGMATE app repo
shouldn't need to run a scheduled data pipeline itself.

## How it works

A GitHub Actions workflow (`.github/workflows/update-wind.yml`) runs 4x/day:

1. Finds the most recently published GFS run (00/06/12/18Z) via NOAA's NOMADS
   GRIB filter service.
2. Downloads just the 10m U/V wind components, globally, at 1° resolution
   (~150KB GRIB2).
3. Converts it to JSON (`convert.py`, using `pygrib`) in the
   `[{header, data}, {header, data}]` shape leaflet-velocity's `L.velocityLayer`
   constructor expects.
4. Commits the result to `docs/wind-global-1deg.json`, served by GitHub Pages.

## Data URL

```
https://aaronyooht.github.io/wingmate-wind-data/wind-global-1deg.json
```

`docs/meta.json` has `refTime` (the GFS analysis time the data is valid for)
and `generatedAt` (when this pipeline last ran).

## Manual run

```
gh workflow run update-wind.yml
```
