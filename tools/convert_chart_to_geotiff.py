"""
Convert a chart PNG + JSON sidecar (latN, latS, lonW, lonE) into a georeferenced image.
- Writes a PNG worldfile (.pgw)
- Attempts to run gdal_translate to make a GeoTIFF (if GDAL is available on PATH)

Usage:
    python tools/convert_chart_to_geotiff.py path/to/chart.png

"""
import sys
import os
import json
from PIL import Image
import subprocess


def write_worldfile(png_path, meta):
    # Worldfile format expects: A, D, B, E, C, F
    # A = pixel size in x (lon per pixel)
    # D = rotation (0)
    # B = rotation (0)
    # E = -pixel size in y (negative: lat decreases down the image)
    # C = x-coordinate of center of top-left pixel (lon)
    # F = y-coordinate of center of top-left pixel (lat)
    img = Image.open(png_path)
    w, h = img.size
    lonW = float(meta['lonW'])
    lonE = float(meta['lonE'])
    latN = float(meta['latN'])
    latS = float(meta['latS'])

    px_w = (lonE - lonW) / float(w)
    px_h = (latN - latS) / float(h)

    A = px_w
    D = 0.0
    B = 0.0
    E = -px_h
    C = lonW + (px_w / 2.0)
    F = latN - (px_h / 2.0)

    world_path = os.path.splitext(png_path)[0] + '.pgw'
    with open(world_path, 'w', encoding='utf-8') as fh:
        fh.write(f"{A:.12f}\n{D:.12f}\n{B:.12f}\n{E:.12f}\n{C:.12f}\n{F:.12f}\n")
    return world_path, (w, h)


def try_gdal_translate(png_path, out_tif, meta):
    # Use gdal_translate with -a_ullr lonMin latMax lonMax latMin and -a_srs EPSG:4326
    lonW = float(meta['lonW'])
    lonE = float(meta['lonE'])
    latN = float(meta['latN'])
    latS = float(meta['latS'])

    cmd = [
        'gdal_translate',
        '-of', 'GTiff',
        '-a_ullr', str(lonW), str(latN), str(lonE), str(latS),
        '-a_srs', 'EPSG:4326',
        png_path, out_tif
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True, proc.stdout + proc.stderr
    except FileNotFoundError:
        return False, 'gdal_translate not found on PATH'
    except subprocess.CalledProcessError as e:
        return False, e.stdout + e.stderr


def main():
    if len(sys.argv) < 2:
        print('Usage: python tools/convert_chart_to_geotiff.py path/to/chart.png')
        return 1
    png_path = sys.argv[1]
    if not os.path.exists(png_path):
        print('File not found:', png_path)
        return 2

    base = os.path.splitext(png_path)[0]
    json_path = base + '.json'
    if not os.path.exists(json_path):
        print('Sidecar JSON not found. Expected:', json_path)
        return 3

    with open(json_path, 'r', encoding='utf-8') as fh:
        meta = json.load(fh)
    required = ('latN','latS','lonW','lonE')
    if not all(k in meta for k in required):
        print('JSON missing required keys (latN,latS,lonW,lonE)')
        return 4

    world_path, size = write_worldfile(png_path, meta)
    print('Wrote worldfile:', world_path, 'image_size:', size)

    out_tif = base + '.tif'
    ok, msg = try_gdal_translate(png_path, out_tif, meta)
    if ok:
        print('GeoTIFF created:', out_tif)
        print(msg)
    else:
        print('Could not create GeoTIFF automatically:', msg)
        print('You can install GDAL (gdal_translate) or use the .pgw worldfile alongside the PNG.')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
