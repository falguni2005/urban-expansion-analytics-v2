# Urban Expansion & Land-Use Analytics Dashboard

A Streamlit dashboard starter with a dark purple UI, interactive city-location map, city/date filters, land-cover charts, urban-expansion comparison, data explorer, CSV export and PDF report.

## Included cities
Pune, Mumbai, Kolhapur, Sangli, Nashik, Nagpur, Solapur, Satara, Thane, Chhatrapati Sambhajinagar, Bengaluru, Hyderabad, New Delhi, Chennai, Ahmedabad, Kolkata, Jaipur, Surat, Indore and Bhopal.

## Important data warning
This ZIP includes CSV files for all 20 cities so every city selector can be tested immediately. **The included land-use areas are synthetic DEMO VALUES**, created only to demonstrate the dashboard's interactions. They are **not** real satellite observations, are not produced by a classifier, and must not be presented as research findings. The dashboard labels these values as demo data. Replace each city's `summary.csv` with real processed observations from your Sentinel/Hadoop/classification workflow before using the results academically.

`data/city_locations.csv` contains approximate city-centre latitude/longitude reference points. The map shows these city-centre points only; it is not a satellite basemap, city boundary, or classified raster. A true land-use map needs georeferenced classification output such as a GeoTIFF or GeoJSON.

## Expected CSV format
Each city's file is under `data/processed_data/cities/<city_slug>/classification/summary.csv` and includes:
- `city`
- `date` (YYYY-MM-DD)
- `class_name`
- `area_square_km`
- `latitude`, `longitude`
- `data_status`

For real results, replace the demo CSVs with the same columns and set `data_status` to a truthful source description, such as `Sentinel-2 classification output`. Keep a record of classifier, date, spatial coverage, resolution and validation accuracy separately for your report.

## Run on Windows
```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m streamlit run app.py
```
Open the local URL printed in the terminal.

## Notes
- Coordinates are approximate city-centre locations.
- City selection and maps work offline only if map rendering libraries/data are local; Plotly's geographic outline may use its bundled geography assets.
- The app currently analyses compatible summary CSV files. It does not automatically download satellite imagery or run a land-cover classifier.


## Windows installation (recommended)

Open Command Prompt in the folder that contains `app.py` and `requirements.txt`, then run:

```bat
py -3.10 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app.py
```

If `py -3.10` is not available, use `python -m venv .venv` instead. Use a virtual environment so globally installed Streamlit/Starlette versions do not conflict.
