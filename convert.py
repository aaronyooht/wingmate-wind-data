#!/usr/bin/env python3
"""GFS GRIB2(10m U/V 바람) -> leaflet-velocity가 읽는 JSON으로 변환한다.

leaflet-velocity/grib2json이 쓰던 스키마를 그대로 따른다 — header에 GRIB2 섹션
메타데이터(괄호 안은 이 파이프라인에서 고정으로 쓰는 값)를 담고, data는 북극(90N,0E)
에서 시작해 동쪽으로, 그다음 위도를 한 칸씩 내려가며(남쪽으로) 나열한 1차원 배열이다.
"""
import json
import sys

import pygrib


def build_header(grb):
    return {
        "discipline": 0,
        "gribEdition": 2,
        "gribLength": 0,
        "center": 7,  # US NCEP
        "subcenter": 0,
        "refTime": grb.analDate.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "significanceOfRT": 1,
        "productStatus": 0,
        "productType": 1,
        "parameterCategory": 2,  # Momentum
        "parameterNumber": grb.parameterNumber,  # 2=U, 3=V
        "parameterUnit": "m.s-1",
        "genProcessType": 2,
        "forecastTime": int(grb.forecastTime),
        "surface1Type": 103,  # Height above ground
        "surface1Value": 10.0,
        "surface2Type": 255,
        "surface2Value": 0,
        "numberPoints": grb.Ni * grb.Nj,
        "shape": 0,
        "scanMode": 0,
        "nx": grb.Ni,
        "ny": grb.Nj,
        "lo1": grb.longitudeOfFirstGridPointInDegrees,
        "la1": grb.latitudeOfFirstGridPointInDegrees,
        "lo2": grb.longitudeOfLastGridPointInDegrees,
        "la2": grb.latitudeOfLastGridPointInDegrees,
        "dx": grb.iDirectionIncrementInDegrees,
        "dy": grb.jDirectionIncrementInDegrees,
    }


def main(grib_path, out_path):
    grbs = pygrib.open(grib_path)
    messages = []
    for grb in grbs:
        # la1(첫 점 위도)이 90에 가까워야(북→남 스캔) leaflet-velocity가 기대하는
        # 순서와 맞는다 — NOMADS GFS는 기본이 이 순서라 보통 뒤집을 필요는 없지만,
        # 혹시 반대로 온 피드를 받더라도 깨지지 않도록 방어적으로 확인한다.
        values = grb.values
        if grb.latitudeOfFirstGridPointInDegrees < grb.latitudeOfLastGridPointInDegrees:
            values = values[::-1]
        messages.append({"header": build_header(grb), "data": values.flatten(order="C").tolist()})

    # leaflet-velocity는 [U메시지, V메시지] 순서를 기대한다.
    messages.sort(key=lambda m: m["header"]["parameterNumber"])

    with open(out_path, "w") as f:
        json.dump(messages, f, separators=(",", ":"))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: convert.py <input.grib2> <output.json>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
