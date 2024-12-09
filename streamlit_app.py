import streamlit as st
import os
from task_management_system import plan_vacation
from datetime import datetime, timedelta
import json

# Set API key from Streamlit secrets
os.environ["TOGETHER_API_KEY"] = st.secrets["TOGETHER_API_KEY"]

# Set page config
st.set_page_config(
    page_title="AI Vacation Planner",
    page_icon="✈️",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton > button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
    }
    .output-container {
        background-color: #f0f2f6;
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

def main():
    st.title("🌴 AI Vacation Planner")
    st.markdown("Let me help you plan your perfect vacation!")

    with st.form("vacation_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Calculate default dates (2 weeks from now for 1 week duration)
            default_start = datetime.now() + timedelta(days=14)
            default_end = default_start + timedelta(days=7)
            
            dates = st.text_input(
                "When do you want to travel?",
                value=f"{default_start.strftime('%B %d')}-{default_end.strftime('%B %d')}, {default_start.year}",
                help="Format: Month Day-Day, Year (e.g., December 20-27, 2024)"
            )
            
            vacation_type = st.selectbox(
                "What type of vacation are you looking for?",
                [
                    "Beach resort, luxury",
                    "Cultural exploration",
                    "Adventure, outdoor",
                    "City tour, shopping",
                    "Wellness retreat"
                ]
            )
            
            mood = st.selectbox(
                "What's your desired mood/vibe?",
                [
                    "Peaceful and romantic",
                    "Adventurous and exciting",
                    "Relaxing and rejuvenating",
                    "Social and lively",
                    "Luxurious and indulgent"
                ]
            )

        with col2:
            budget = st.number_input(
                "What's your total budget? (USD)",
                min_value=1000,
                max_value=50000,
                value=5000,
                step=500,
                help="Total budget for the entire trip"
            )
            
            location = st.text_input(
                "Any location preferences?",
                placeholder="e.g., somewhere in the Caribbean, Europe, Southeast Asia",
                help="Enter your preferred destination or region"
            )
            
            notes = st.text_area(
                "Additional notes or requirements",
                placeholder="e.g., must have good vegetarian food options, prefer boutique hotels, interested in local cooking classes",
                help="Any special requirements or interests?"
            )

        submitted = st.form_submit_button("Plan My Vacation! 🎯")

    if submitted:
        try:
            with st.spinner("Planning your perfect vacation... ✨"):
                # Format the request
                vacation_request = f"""
                I want to plan a {vacation_type} vacation:
                - Dates: {dates}
                - Type: {vacation_type}
                - Vibe: {mood}
                - Budget: ${budget} total
                - Preference: {location}
                Additional Notes: {notes}
                """
                
                # Get the vacation plan
                result = plan_vacation(vacation_request)
                
                # Display the results in a nice format
                st.success("Your vacation plan is ready! 🎉")
                
                # Create tabs for different sections
                details_tab, activities_tab, dining_tab = st.tabs([
                    "Vacation Details", 
                    "Daily Activities", 
                    "Restaurant Recommendations"
                ])
                
                with details_tab:
                    if "vacation_details" in result:
                        details = result["vacation_details"]
                        st.subheader("Vacation Overview")
                        cols = st.columns(2)
                        with cols[0]:
                            st.write("🌍 **Location:**", details.get("location", location))
                            st.write("📅 **Duration:**", details.get("duration", "As specified"))
                            st.write("💰 **Budget Allocation:**", details.get("budget_allocation", f"Total: ${budget}"))
                        with cols[1]:
                            st.write("🎯 **Trip Style:**", vacation_type)
                            st.write("✨ **Vibe:**", mood)
                            if "highlights" in details:
                                st.write("✨ **Highlights:**", details["highlights"])
                
                with activities_tab:
                    if "itinerary" in result and "daily_activities" in result["itinerary"]:
                        st.subheader("Daily Itinerary")
                        for day, activities in result["itinerary"]["daily_activities"].items():
                            with st.expander(f"Day {day}"):
                                if isinstance(activities, dict):
                                    for time, activity in activities.items():
                                        st.write(f"**{time}:** {activity}")
                                else:
                                    st.write(activities)
                
                with dining_tab:
                    if "restaurant_bookings" in result:
                        st.subheader("Restaurant Recommendations")
                        for restaurant in result["restaurant_bookings"]:
                            with st.expander(restaurant.get("name", "Restaurant")):
                                st.write("🍽️ **Cuisine:**", restaurant.get("cuisine", "Various"))
                                st.write("💰 **Price Range:**", restaurant.get("price_range", "Unknown"))
                                st.write("⭐ **Rating:**", restaurant.get("rating", "N/A"))
                                st.write("📝 **Description:**", restaurant.get("description", ""))

        except Exception as e:
            st.error(f"An error occurred while planning your vacation: {str(e)}")
            st.write("Please try again with different inputs or contact support if the issue persists.")

if __name__ == "__main__":
    main()
