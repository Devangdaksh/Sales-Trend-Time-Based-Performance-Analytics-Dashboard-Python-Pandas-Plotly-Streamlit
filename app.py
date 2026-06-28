# -------------------------------
# Importing Libraries
# --------------------------------

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from sklearn.preprocessing import LabelEncoder
import warnings

warnings.filterwarnings("ignore")

# -------------------------------
# Theme, layout, sidebar
# --------------------------------
st.set_page_config(
    page_title="Coffee Sales Performance Dashboard",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded",
)