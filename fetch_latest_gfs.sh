#!/bin/bash
# 가장 최근에 실제로 공개된 GFS run을 찾아 10m U/V 바람(전지구, 1도 해상도) GRIB2를
# 받는다. GFS는 00/06/12/18Z에 도는데 공개까지 보통 3~5시간이 걸려서, "지금 시각"에서
# 바로 최신 사이클을 요청하면 아직 안 나와 있을 수 있다 — 최근 것부터 거슬러 올라가며
# 실제로 받아지는 첫 번째 사이클을 쓴다.
set -euo pipefail

OUT="${1:-gfs.grib2}"
CYCLES=(18 12 06 00)

for offset in 0 1; do
  DATE=$(date -u -d "-${offset} day" +%Y%m%d)
  for cycle in "${CYCLES[@]}"; do
    URL="https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_1p00.pl?file=gfs.t${cycle}z.pgrb2.1p00.f000&lev_10_m_above_ground=on&var_UGRD=on&var_VGRD=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fgfs.${DATE}%2F${cycle}%2Fatmos"
    echo "[fetch] trying ${DATE} ${cycle}Z ..." >&2
    if curl -sf --max-time 60 "$URL" -o "$OUT" && [ -s "$OUT" ] && file "$OUT" | grep -q "GRIB"; then
      echo "[fetch] got ${DATE} ${cycle}Z" >&2
      echo "${DATE}T${cycle}:00:00Z"
      exit 0
    fi
  done
done

echo "[fetch] no available GFS cycle found in the last 2 days" >&2
exit 1
