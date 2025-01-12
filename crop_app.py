import streamlit as st
import pickle
import numpy as np
import base64
from sklearn.preprocessing import LabelEncoder

# Load the trained model
with open("crop_yield_model.pkl", "rb") as file:
    model = pickle.load(file)

# Initialize encoders
soil_type_encoder = LabelEncoder()
crop_type_encoder = LabelEncoder()

soil_types = ['Loamy', 'Alluvial', 'Clayey', 'Sandy', 'Silty']  # Replace with your actual soil types
crop_types = ['Wheat', 'Rice', 'Bajra', 'Sugarcane', 'Maize', 'Millet', 'Barley', 'Soybean']  # Replace with your actual crop types

# Fit the encoders
soil_type_encoder.fit(soil_types)
crop_type_encoder.fit(crop_types)


# Conversion function
def convert_hectares_to_acres(size_hectares):
    return size_hectares * 2.47

def calculate_sacks(yield_kg, sack_size_kg=50):
    return yield_kg / sack_size_kg

# Add custom CSS for background
def add_background(image_path):
    # Open image in binary mode and encode to Base64
    with open(image_path, "rb") as file:
        encoded_image = base64.b64encode(file.read()).decode('utf-8')  # Base64 encoding
    
    # Use Base64-encoded string in the CSS background property
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded_image}");
            background-size: cover;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# Add custom CSS for input field colors
def style_inputs():
    st.markdown(
        """
        <style>
        /* Style for input fields */
        input[type="number"], input[type="text"], select {
            background-color: rgba(255, 255, 255, 0.9); /* Slightly transparent white */
            color: black; /* Black text */
            border: 3px solid #4CAF50; /* Thick green border */
            border-radius: 8px; /* More rounded corners */
            padding: 12px; /* Larger padding for better visibility */
            font-size: 16px; /* Larger font size */
            font-weight: bold; /* Bold text for better readability */
        }

        /* Style for buttons */
        button {
            background-color: #4CAF50; /* Green background */
            color: white; /* White text */
            border: none;
            padding: 12px 24px; /* Bigger padding for a prominent look */
            font-size: 18px; /* Larger font size */
            font-weight: bold; /* Bold text */
            cursor: pointer;
            border-radius: 8px; /* More rounded corners */
        }
        button:hover {
            background-color: #45a049; /* Darker green on hover */
        }
        
        /* Style for other text-based inputs like select boxes */
        .stNumberInput, .stSelectbox {
            background-color: rgba(255, 255, 255, 0.9); /* Slightly transparent */
            font-size: 16px; /* Larger font size */
            font-weight: bold; /* Bold text */
            color: black; /* Black text for readability */
            border: 3px solid #4CAF50; /* Consistent border style */
            border-radius: 8px; /* Rounded corners */
            padding: 10px; /* Comfortable padding */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# Call background function with your image
add_background("crops-growing-in-thailand.jpg")

# Crop recommendations based on soil type
crop_recommendations = {
    'Loamy': ['Wheat', 'Rice', 'Bajra'],
    'Alluvial': ['Wheat', 'Rice'],
    'Clayey': ['Sugarcane', 'Paddy'],
    'Sandy': ['Maize', 'Millet'],
    'Silty': ['Barley', 'Soybean']
}

# Streamlit app design
st.title("🌾 Farmer-Friendly Crop Yield Predictor")

# Inputs
soil_type = st.selectbox("Select Soil Type:", list(crop_recommendations.keys()))
st.write(f"Recommended Crops for {soil_type}: {', '.join(crop_recommendations[soil_type])}")

crop_type = st.selectbox("Select Crop Type:", crop_recommendations[soil_type])
year = st.number_input("Enter Year:", min_value=2000, max_value=2030, value=2023, step=1)

irrigation_area = st.number_input("Enter Irrigated Area (in hectares):", min_value=0.0, value=0.0, step=0.1)
irrigation_area_acres = convert_hectares_to_acres(irrigation_area)
st.write(f"Irrigated Area: {irrigation_area_acres:.2f} acres")

# Default MSP if not in dataset
default_msp = 100.0  # Example default value for MSP
msp = st.number_input("Enter Minimum Support Price (MSP) (₹/kg):", min_value=0.0, value=default_msp, step=1.0)

sack_size = st.number_input("Enter Sack Size (kg):", min_value=50, max_value=100, value=50, step=5)

# Streamlit app design
if st.button("Predict Yield"):
     # Encode categorical inputs
    encoded_soil_type = soil_type_encoder.transform([soil_type])[0]
    encoded_crop_type = crop_type_encoder.transform([crop_type])[0]

    # Prepare input for prediction
    input_features = np.array([[year, irrigation_area, encoded_soil_type, encoded_crop_type]])
   

    # Prepare input for prediction
    
    predicted_yield_per_ha = model.predict(input_features)[0]
    total_yield_kg = irrigation_area * predicted_yield_per_ha
    total_revenue = total_yield_kg * msp
    total_sacks = calculate_sacks(total_yield_kg, sack_size)

     # Display results with custom styling
    st.markdown(
        f"""
        <p style="color:black; font-weight:bold;">
            Predicted Yield: {total_yield_kg:.2f} kg
        </p>
        <p style="color:black; font-weight:bold;">
            Equivalent Sacks: {total_sacks:.0f} sacks
        </p>
        <p style="color:black; font-weight:bold;">
            Estimated Revenue: ₹{total_revenue:,.2f}
        </p>
        """,
        unsafe_allow_html=True
    )


    # Display results
    #st.success(f"Predicted Yield: {total_yield_kg:.2f} kg")
    #st.success(f"Equivalent Sacks: {total_sacks:.0f} sacks")
    #st.success(f"Estimated Revenue: ₹{total_revenue:,.2f}")
