# K-Means Clustering of Geo-Coded Watershed Imagery for Development Outcome Zoning

**Study area:** Entire Himachal Pradesh, India  
**Academic level:** Third-year BTech CSE  
**Stack:** Python, Google Earth Engine, Sentinel-2, SRTM, JRC Global Surface Water, scikit-learn, Streamlit.

## 1. Project scope

This prototype extracts terrain, vegetation and surface-water indicators from satellite imagery, clusters spatial samples using K-Means, compares alternative clustering methods, and displays indicative priority zones.

**Important spatial-unit note:** The first version samples statewide spatial points. These are not official watershed polygons. For true watershed-level zoning, add a validated watershed boundary layer and calculate zonal statistics for each polygon.

**Important validation note:** The included field-outcome scores are synthetic demo data, not actual field observations or government records. Replace them with independently collected field/project-monitoring data before making external-validation claims.

## 2. Data sources

- Sentinel-2 Surface Reflectance Harmonized: `COPERNICUS/S2_SR_HARMONIZED` in Earth Engine.
- SRTM elevation: `USGS/SRTMGL1_003`.
- Surface-water occurrence: `JRC/GSW1_4/GlobalSurfaceWater`.
- Himachal Pradesh administrative boundary: FAO GAUL 2015 level 1.

Features: elevation (m), slope (degrees), NDVI, NDWI (Green-NIR), water occurrence (%) and local terrain range (m).

## 3. Installation

Use Python 3.10 or 3.11.

### Windows
```bash
py -3.11 -m venv .venv
.venv\\Scripts\\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### macOS / Linux
```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Run immediately using sample data

```bash
python -m src.sample_data
streamlit run app.py
```

Open the local Streamlit URL, normally `http://localhost:8501`. The dashboard will use synthetic demonstration data if no real CSV is present.

## 5. Export real satellite-derived features

1. Create a Google Cloud project and register it for Earth Engine.
2. Follow the current Google Earth Engine access and authentication instructions.
3. Authenticate:
```bash
earthengine authenticate
```
4. Run the export:
```bash
python -m src.gee_export --project YOUR_GEE_CLOUD_PROJECT --start 2023-01-01 --end 2025-12-31 --scale 5000 --points 2500
```
5. Monitor the task in the Earth Engine Tasks panel or Google Drive. The export folder is `Watershed_Development_Zoning`.
6. Download `himachal_pradesh_features.csv` into `data/raw/himachal_pradesh_features.csv`.
7. Restart the dashboard or upload the CSV using the sidebar.

The export uses a simplified QA60 cloud mask and a multi-year median composite. For a research-quality study, improve cloud masking with Sentinel-2 cloud probability, compare seasonal composites, inspect snow/shadow effects, and verify the boundary and sample coverage.

## 6. Dashboard features

- CSV upload and dataset preview.
- Configurable K-Means K and initialization.
- Interactive map of indicative zones.
- Cluster feature profiles.
- K-Means versus Ward hierarchical clustering and DBSCAN.
- Optional K-Medoids (PAM) if `scikit-learn-extra` is installed.
- Elbow curve, inertia, silhouette and Davies-Bouldin metrics.
- CSV download and model saving.

## 7. Machine-learning methodology

### Preprocessing
Median imputation handles missing values. StandardScaler is applied because elevation and terrain values have much larger numeric ranges than normalized indices.

### K-Means
The primary model uses K-Means with configurable K and random or K-Means++ initialization. K-Means++ is the recommended default. The objective minimizes within-cluster sum of squared distances (WCSS).

### Validation
- Inertia / WCSS: decreases as K increases; never use it alone.
- Silhouette: higher is generally better.
- Davies-Bouldin: lower is generally better.
- Elbow method: heuristic, not proof of an optimal K.

### Comparative methods
- Agglomerative hierarchical clustering with Ward linkage.
- DBSCAN with epsilon and minimum samples.
- Optional K-Medoids (PAM).
- MiniBatchKMeans is implemented as an option in `src/clustering.py`.

## 8. Priority-zone interpretation

K-Means cluster numbers are arbitrary. The application ranks clusters using an illustrative intervention score based on low NDVI, low water occurrence, high slope and high local terrain range. The weights are demonstration assumptions, not validated policy thresholds. Review them with watershed experts before using the zones for planning.

## 9. External validation

For genuine validation:
1. Obtain field survey or official watershed-project monitoring data with coordinates/watershed IDs and dates.
2. Document source, measurement units, collection method and missing data.
3. Spatially join the observations to analysis units.
4. Keep outcome columns out of the clustering feature matrix to avoid leakage.
5. Compare outcome distributions across clusters, including confidence intervals and suitable statistical tests.
6. Use spatially separated validation regions where possible.

The synthetic sample score only demonstrates the software workflow. It is not evidence of real development outcomes.

## 10. Limitations

- Statewide sample points are not official watershed polygons.
- Five-kilometre sampling is for a prototype, not fine-grained local planning.
- NDWI can be affected by snow, shadow and dark surfaces.
- JRC occurrence measures detected surface water, not groundwater availability.
- NDVI varies by season, crop cycle, snow and elevation.
- K-Means assumes distance-based, roughly compact clusters and is sensitive to outliers and scaling.
- Spatial autocorrelation means nearby points are not independent.

## 11. Suggested experiments

1. Compare K=2 through 8 using WCSS, silhouette and Davies-Bouldin.
2. Compare random and K-Means++ initialization.
3. Compare raw and standardized features.
4. Compare K-Means, Ward hierarchical clustering and DBSCAN.
5. Interpret cluster feature profiles and spatial maps.
6. Replace synthetic outcomes with independent field outcomes and evaluate external agreement.

## 12. Report structure

1. Abstract
2. Introduction
3. Problem Statement and Objectives
4. Literature Review
5. Study Area and Dataset
6. Feature Extraction and Preprocessing
7. Clustering Algorithms
8. Experimental Setup
9. Results and Discussion
10. External Validation
11. Limitations
12. Conclusion and Future Scope
13. References

## 13. Future scope

- Use validated watershed boundaries and calculate polygon-level zonal statistics.
- Add seasonal vegetation/water trends, rainfall, soil, land-use and hydrological layers.
- Add spatial cross-validation and uncertainty estimates.
- Compare clusters against actual WDC-PMKSY project outcomes.

## References / useful portals

- Copernicus Data Space: https://dataspace.copernicus.eu/
- Earth Engine Data Catalog: https://developers.google.com/earth-engine/datasets
- USGS SRTM: https://www.usgs.gov/centers/eros/science/usgs-eros-archive-digital-elevation-shuttle-radar-topography-mission-srtm-1
- scikit-learn clustering: https://scikit-learn.org/stable/modules/clustering.html
- WDC-PMKSY: https://www.wdcpmksy.dolr.gov.in/
