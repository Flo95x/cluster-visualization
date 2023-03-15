from typing import List

import streamlit as st
import pandas as pd
from sklearn.preprocessing import StandardScaler

from constants import CLUSTER_ALGORITHMS, DATASET_NAMES, MAX_PLOTS_PER_ROW
from utils.preparation import get_default_dataset_points, get_cluster_algo_parameters, add_user_data_input_listener, split_list
from utils.modeling import get_cluster_labels
from utils.visualization import plot_figure
from data_classes import DatasetName

# TODO: Customize icon
st.set_page_config(
    page_title="ikneed",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)



def main():
    """
    The main function
    """

    st.sidebar.write("Either upload csv file, or use one of the example datasets")
    uploaded_file = st.sidebar.file_uploader("CSV File", type="csv")
    if uploaded_file is not None:
        dataset_name = DatasetName.CUSTOM.value
        # Can be used wherever a "file-like" object is accepted:
        df = pd.read_csv(uploaded_file)
        if df.shape[1] not in [2,3]:
            raise ValueError(f"Only 2 or 3 dimensional features are allowed, but csv file contains {df.shape[1]} features")
        default_dataset_points = df.iloc[:,0:3].to_numpy()
    else:
        st.sidebar.subheader("Example Dataset")
        is_3d = st.sidebar.checkbox("Use 3D Features", value=False)
        dataset_name = st.sidebar.selectbox(
            "Default Data", [dn.value for dn in DATASET_NAMES])
        default_dataset_points = get_default_dataset_points(dataset_name, is_3d)

    cluster_features = add_user_data_input_listener(default_dataset_points)
    # normalize dataset for easier parameter selection
    cluster_features_scaled = StandardScaler().fit_transform(cluster_features)

    st.title("Cluster Visualization")
    st.write("Streamlit application of the [sklearn cluster comparison](https://scikit-learn.org/stable/modules/clustering.html) page. \n"
             "Feel free to upload your own custom data or to play around with one of the example datasets. The cluster algorithm parameters can interactivly be updated and three dimensional visualizations are possible as well.")
    st.write("[Source code](https://github.com/FloTeu/cluster-visualization)")

    # Cluster Algo
    cluster_algos: List[str] = st.sidebar.multiselect(
        "Cluster Algorithms", [ca.value for ca in CLUSTER_ALGORITHMS], [CLUSTER_ALGORITHMS[0]])
    for cluster_algo_splitted_list in split_list(cluster_algos, MAX_PLOTS_PER_ROW):
        display_cols = st.columns(MAX_PLOTS_PER_ROW)
        for i, cluster_algo_str in enumerate(cluster_algo_splitted_list):
            st.sidebar.title(cluster_algo_str)
            cluster_algo_kwargs = get_cluster_algo_parameters(cluster_algo_str, cluster_features_scaled, dataset_name)
            cluster_labels = get_cluster_labels(cluster_features_scaled, cluster_algo_str, **cluster_algo_kwargs)

            # plot the figure
            display_cols[i].subheader(cluster_algo_str)

            fig = plot_figure(cluster_features,cluster_labels)
            # prevent that on visualization does not take the whole width
            use_container_width = len(cluster_algos) > 1
            display_cols[i].plotly_chart(fig, use_container_width=use_container_width)





if __name__ == "__main__":
    main()
