import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
from src.config import FEATURES, MODELS, REPORTS
from src.data_loader import load_dataset
from src.preprocessing import prepare_features
from src.clustering import fit_kmeans, compare_algorithms
from src.validation import internal_metrics, elbow_values, outcome_validation
from src.zoning import assign_priority_zones

st.set_page_config(page_title="Himachal Watershed Zoning",page_icon="🏔️",layout="wide")
st.title("🏔️ Himachal Pradesh Watershed Development Zoning")
st.caption("Geo-coded satellite feature analysis | Unsupervised Machine Learning")

with st.sidebar:
    st.header("Project controls")
    uploaded=st.file_uploader("Upload feature CSV",type=["csv"])
    k=st.slider("Number of clusters (K)",2,8,3)
    init=st.selectbox("K-Means initialization",["k-means++","random"])
    view=st.radio("Analysis view",["K-Means zoning","Algorithm comparison","Cluster validation"])

df,source=load_dataset(uploaded)
missing=[c for c in FEATURES if c not in df.columns]
if missing:
    st.error(f"Missing required columns: {missing}")
    st.stop()
st.warning(f"Dataset mode: {source}. Synthetic outcomes are not real field reports.")
a,b,c,d=st.columns(4)
a.metric("Samples",f"{len(df):,}")
b.metric("Features",len(FEATURES))
c.metric("Latitude span",f"{df.latitude.min():.2f}° to {df.latitude.max():.2f}°" if "latitude" in df else "N/A")
d.metric("Longitude span",f"{df.longitude.min():.2f}° to {df.longitude.max():.2f}°" if "longitude" in df else "N/A")
with st.expander("Dataset preview and feature definitions"):
    st.dataframe(df.head(20),use_container_width=True)
    st.write("NDVI: vegetation indicator; NDWI: Green-NIR water indicator; water occurrence: historical surface-water occurrence; terrain range: local elevation range.")

X,imputer,scaler=prepare_features(df)
model,labels=fit_kmeans(X,k,init)
base=df.copy()
base["cluster"]=labels
zoned=assign_priority_zones(base)
metrics=internal_metrics(X,labels,model.inertia_)

if view=="K-Means zoning":
    st.subheader("Indicative development-priority zones")
    left,right=st.columns([1.5,1])
    with left:
        if {"latitude","longitude"}.issubset(zoned.columns):
            fig=px.scatter_mapbox(zoned,lat="latitude",lon="longitude",
                color="priority_zone",hover_data=["cluster","ndvi","slope_deg","water_occurrence"],
                zoom=6,height=560,mapbox_style="open-street-map")
            st.plotly_chart(fig,use_container_width=True)
        else:
            st.info("Latitude and longitude are needed for the map.")
    with right:
        st.metric("Inertia (WCSS)",f"{model.inertia_:,.2f}")
        st.metric("Silhouette",f"{metrics['silhouette']:.3f}" if metrics["silhouette"] is not None else "N/A")
        st.metric("Davies-Bouldin",f"{metrics['davies_bouldin']:.3f}" if metrics["davies_bouldin"] is not None else "N/A")
        st.write("Cluster feature profiles")
        st.dataframe(zoned.groupby(["cluster","priority_zone"])[FEATURES].mean().round(3),use_container_width=True)
    st.download_button("Download zoned CSV",zoned.to_csv(index=False),"himachal_watershed_zones.csv","text/csv")
elif view=="Algorithm comparison":
    rows=[]
    for name,lab in compare_algorithms(X,k).items():
        rows.append({"Algorithm":name,**internal_metrics(X,lab)})
    st.subheader("Clustering algorithm comparison")
    st.dataframe(pd.DataFrame(rows),use_container_width=True)
    st.caption("DBSCAN noise points are labelled -1. Metrics are computed on non-noise points where valid.")
else:
    st.subheader("Cluster validation")
    elbow=pd.DataFrame(elbow_values(X,2,min(10,len(X)-1)))
    st.plotly_chart(px.line(elbow,x="k",y="inertia",markers=True,title="Elbow analysis: K versus WCSS"),use_container_width=True)
    st.json(metrics)
    outcome=outcome_validation(zoned)
    if outcome is not None:
        st.write("Outcome score summary by cluster")
        st.dataframe(outcome,use_container_width=True)
        st.caption("Replace synthetic outcomes with independent field measurements before claiming external validation.")
    else:
        st.info("No field_outcome_score found. Add independently measured outcomes to enable external validation.")

st.divider()
st.subheader("Interpretation and limitations")
st.markdown("- Cluster IDs are arbitrary and are not development categories by themselves.\n- Priority labels use an illustrative score: low NDVI and water occurrence, high slope and terrain variability increase the score.\n- Satellite indicators do not directly measure groundwater, household welfare, irrigation access or project completion.\n- This is a student decision-support prototype, not an official planning tool.")
if st.button("Save model and results"):
    MODELS.mkdir(exist_ok=True)
    REPORTS.mkdir(parents=True,exist_ok=True)
    joblib.dump({"model":model,"imputer":imputer,"scaler":scaler,"features":FEATURES},MODELS/"kmeans_pipeline.pkl")
    zoned.to_csv(REPORTS/"latest_zoning_results.csv",index=False)
    st.success("Saved model and zoning CSV.")
