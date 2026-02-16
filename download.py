import cdsapi

url= "https://cds.climate.copernicus.eu/api"
key= "f4a1470f-76fc-430d-adb6-656b93c412ef"

client = cdsapi.Client(url=url, key=key)

dataset = "reanalysis-era5-land"
request = {
    "variable": [
        "10m_u_component_of_wind",
        "10m_v_component_of_wind"
    ],
    "year": "2026",
    "month": "02",
    "day": ["02"],
    "time": ["02:00"],
    "data_format": "netcdf",
    "download_format": "unarchived",
    "area": [38,60,22,90]
}
client.retrieve(dataset, request).download()