import xarray as xr
import numpy as np
from tqdm import tqdm
from numba import njit

# =========================
# LOAD DATA
# =========================

TIME = '2026-02-02T02:00:00'

ds = xr.open_dataset('ee55fbf506dcf538ff0520dd455676d5.nc')

u_field = ds['u10'].values
v_field = ds['v10'].values

lat_grid = ds['latitude'].values
lon_grid = ds['longitude'].values

dlat = lat_grid[1] - lat_grid[0]
dlon = lon_grid[1] - lon_grid[0]

lat0 = lat_grid[0]
lon0 = lon_grid[0]

nlat = len(lat_grid)
nlon = len(lon_grid)

# =========================
# INITIALIZE PARTICLES
# =========================

lat_list = []
lon_list = []

for lat1000 in range(28500, 28800):
    for lon1000 in range(77000, 77300):
        lat_list.append(lat1000 / 1000)
        lon_list.append(lon1000 / 1000)

lat = np.array(lat_list)
lon = np.array(lon_list)

# =========================
# BILINEAR INTERPOLATION
# =========================


@njit
def interp_bilinear(field, lat, lon, lat0, lon0, dlat, dlon, nlat, nlon):
    n = len(lat)
    result = np.empty(n, dtype=np.float32)

    for k in range(n):
        i = (lat[k] - lat0) / dlat
        j = (lon[k] - lon0) / dlon

        i0 = int(np.floor(i))
        j0 = int(np.floor(j))

        if i0 < 0:
            i0 = 0
        if i0 > nlat - 2:
            i0 = nlat - 2

        if j0 < 0:
            j0 = 0
        if j0 > nlon - 2:
            j0 = nlon - 2

        di = i - i0
        dj = j - j0

        f00 = field[i0, j0]
        f01 = field[i0, j0 + 1]
        f10 = field[i0 + 1, j0]
        f11 = field[i0 + 1, j0 + 1]

        result[k] = (
            f00 * (1 - di) * (1 - dj) +
            f01 * (1 - di) * dj +
            f10 * di * (1 - dj) +
            f11 * di * dj
        )

    return result
# =========================
# SIMULATION LOOP
# =========================


dt = 36000
steps = 1000

u_field = u_field[0]
v_field = v_field[0]

print("u_field shape:", u_field.shape)
print("v_field shape:", v_field.shape)
print("dtype:", u_field.dtype)


for _ in tqdm(range(steps)):

    uval = interp_bilinear(
        u_field, lat, lon,
        lat0, lon0, dlat, dlon,
        nlat, nlon
    )

    vval = interp_bilinear(
        v_field, lat, lon,
        lat0, lon0, dlat, dlon,
        nlat, nlon
    )

    meters_per_deg_lat = 111_320
    meters_per_deg_lon = 111_320 * np.cos(np.deg2rad(lat))

    lat -= (vval * dt) / meters_per_deg_lat
    lon -= (uval * dt) / meters_per_deg_lon

# =========================
# OUTPUT
# =========================

latsandlongs = []

for i in range(len(lat)):
    latsandlongs.append((int(lat[i]), int(lon[i])))

latsandlongs = set(latsandlongs)
print(latsandlongs)
