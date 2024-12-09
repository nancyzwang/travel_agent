from typing import TypedDict, Annotated, Sequence, Dict, Optional
from datetime import datetime
from langgraph.graph import Graph, StateGraph
from langchain_core.messages import HumanMessage, AIMessage
import together
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import operator
from dotenv import load_dotenv
import os
import json
import requests

# Load environment variables
load_dotenv()

# Initialize Together.ai API key
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "72485359b7b96fc4c31a44e232cf4b0608c60c5d8b8123f892836192a168c540")
print(f"Using Together API key: {TOGETHER_API_KEY[:8]}...")  # Only print first 8 characters for security

# Define our state
class VacationState(TypedDict):
    messages: Sequence[HumanMessage | AIMessage]
    vacation_details: Dict
    itinerary: Dict
    restaurant_bookings: list
    current_step: str
    step_status: Dict[str, str]
    errors: list

def chat_completion(prompt: str) -> str:
    """Helper function to get chat completion from Together.ai"""
    try:
        print("Making API request to Together.ai...")
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "prompt": f"""<s>[INST] You are a helpful vacation planning assistant. Please respond in valid JSON format.

{prompt} [/INST]""",
            "max_tokens": 1024,
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
        }
        
        print("Sending request...")
        response = requests.post(
            "https://api.together.xyz/inference",
            headers=headers,
            json=data
        )
        
        print(f"Response status code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            response_text = result['output']['choices'][0]['text']
            print(f"Got successful response: {response_text[:100]}...")  # Print first 100 chars
            return response_text
        else:
            print(f"API request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return "{}"
            
    except Exception as e:
        print(f"Error in chat completion: {str(e)}")
        return "{}"  # Return empty JSON object as fallback

def analyze_vacation_request(state: VacationState) -> VacationState:
    """Analyze the vacation request and extract key details."""
    print("\nStarting analyze_vacation_request...")
    
    # Initialize state if needed
    if "errors" not in state:
        state["errors"] = []
    if "step_status" not in state:
        state["step_status"] = {}
    
    message = state.get("messages", [])[0].content
    print(f"Analyzing message: {message}")
    
    prompt = f"""Analyze this vacation request and extract the key details. 
    Request: {message}
    
    Format your response as a valid JSON object with this structure:
    {{
        "location": string,
        "dates": string,
        "duration": number,
        "type": string,
        "mood": string,
        "budget": string,
        "preferences": [string]
    }}
    """
    
    print("Sending request to Together.ai...")
    response = chat_completion(prompt)
    print("Got response: ", response)
    
    try:
        # Clean the response to ensure it's valid JSON
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()
        
        details = json.loads(response)
        state["vacation_details"] = details
        state["step_status"]["analyze"] = "completed"
    except json.JSONDecodeError as e:
        print(f"Error parsing vacation details: {e}")
        state["step_status"]["analyze"] = "failed"
        state["errors"].append(f"Failed to parse vacation details: {str(e)}")
    
    return state

def plan_itinerary(state: VacationState) -> VacationState:
    """Generate a detailed itinerary based on the analyzed vacation request."""
    print("\nStarting plan_itinerary...")
    
    # Initialize errors list if not present
    if "errors" not in state:
        state["errors"] = []
    
    location = state["vacation_details"]["location"]
    mood = state["vacation_details"]["mood"]
    duration = state["vacation_details"]["duration"]
    
    print(f"Planning {duration}-day {mood} itinerary in {location}")
    
    # First, get a simple structure for one day
    prompt = f"""Create a detailed itinerary for DAY 1 ONLY of a luxury vacation in {location}.
    
    RESPOND WITH ONLY A JSON OBJECT. NO OTHER TEXT OR MARKDOWN.
    ALL PROPERTY NAMES AND STRING VALUES MUST USE DOUBLE QUOTES.
    
    Required structure:
    {{
        "day": 1,
        "activities": [
            {{
                "time_slot": "morning",
                "activity": "Sunrise Yoga Session",
                "description": "Private beachfront yoga class",
                "vendor": {{
                    "name": "Four Seasons Resort Bali",
                    "phone": "+62 361 701010",
                    "address": "Jimbaran, Bali 80361, Indonesia",
                    "website": "fourseasons.com/bali",
                    "email": "spa.bali@fourseasons.com"
                }},
                "booking_details": {{
                    "duration": "90 minutes",
                    "advance_booking_required": true,
                    "what_to_bring": ["Comfortable clothing", "Water bottle"],
                    "dress_code": "Athletic wear",
                    "fitness_level": "All levels"
                }},
                "estimated_cost": "$150"
            }}
        ]
    }}
    
    Include luxury activities that match these preferences: {state["vacation_details"]["preferences"]}.
    Stay within a daily budget of {int(state["vacation_details"]["budget"][1:])/duration} USD.
    """

    print("Requesting day 1 itinerary...")
    day1_response = chat_completion(prompt)
    
    try:
        # Clean and parse day 1
        day1_response = day1_response.strip()
        if day1_response.startswith("```json"):
            day1_response = day1_response[7:]
        if day1_response.endswith("```"):
            day1_response = day1_response[:-3]
        day1_response = day1_response.strip()
        
        day1 = json.loads(day1_response)
        
        # Now create the full itinerary structure
        itinerary = {
            "location": location,
            "mood": mood,
            "num_days": duration,
            "daily_activities": []
        }
        
        # Add day 1
        itinerary["daily_activities"].append(day1)
        
        # For each remaining day, modify the prompt slightly
        for day in range(2, duration + 1):
            day_prompt = f"""Create a detailed itinerary for DAY {day} of the luxury vacation in {location}.
            Use the same JSON structure as before, but with "day": {day}.
            Include different activities than previous days.
            Stay within daily budget of {int(state["vacation_details"]["budget"][1:])/duration} USD.
            Focus on: {state["vacation_details"]["preferences"]}
            """
            
            day_response = chat_completion(day_prompt)
            day_response = day_response.strip()
            if day_response.startswith("```json"):
                day_response = day_response[7:]
            if day_response.endswith("```"):
                day_response = day_response[:-3]
            day_response = day_response.strip()
            
            day_data = json.loads(day_response)
            itinerary["daily_activities"].append(day_data)
        
        print("Successfully created full itinerary")
        state["itinerary"] = itinerary
        state["step_status"]["plan_itinerary"] = "completed"
        
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error with itinerary: {e}")
        state["step_status"]["plan_itinerary"] = "failed"
        state["errors"].append(f"Failed to process itinerary: {str(e)}")
        # Initialize empty itinerary structure
        state["itinerary"] = {
            "location": location,
            "mood": mood,
            "num_days": duration,
            "daily_activities": []
        }
    
    return state

def book_restaurants(state: VacationState) -> VacationState:
    """Suggest restaurants based on the itinerary and integrate them into the daily schedule."""
    try:
        print("\nStarting restaurant suggestions...")
        if "error" in state["itinerary"]:
            print("Skipping restaurant suggestions due to itinerary error")
            state["step_status"]["book_restaurants"] = "skipped"
            state["current_step"] = "end"
            return state
            
        location = state["itinerary"].get("location", "")
        mood = state["itinerary"].get("mood", "")
        daily_activities = state["itinerary"].get("daily_activities", [])
        
        print(f"Finding restaurants in {location} to complement daily activities")
        
        # First get AI suggestions with strict JSON formatting
        prompt = f"""Suggest exactly 3 high-end restaurants for this luxury vacation in {location}.
        Mood: {mood}
        
        Provide ONLY a JSON response in this EXACT format, with NO additional text:
        {{
            "restaurants": [
                {{
                    "name": "Restaurant Name",
                    "cuisine": "Cuisine Type",
                    "price_range": "$$$$",
                    "address": "Full Address",
                    "phone": "+1234567890",
                    "hours": {{
                        "monday": "11:30 AM - 10:00 PM",
                        "tuesday": "11:30 AM - 10:00 PM",
                        "wednesday": "11:30 AM - 10:00 PM",
                        "thursday": "11:30 AM - 10:00 PM",
                        "friday": "11:30 AM - 10:00 PM",
                        "saturday": "11:30 AM - 10:00 PM",
                        "sunday": "11:30 AM - 10:00 PM"
                    }},
                    "dress_code": "Smart Casual/Formal",
                    "signature_dishes": ["Dish 1", "Dish 2"],
                    "best_time": "dinner",
                    "reservation_notes": "Reservations required"
                }}
            ]
        }}
        """
        
        print("Requesting restaurant suggestions...")
        response = chat_completion(prompt)
        
        try:
            data = json.loads(response)
            restaurants = data.get("restaurants", [])
            print(f"Successfully parsed {len(restaurants)} restaurant suggestions")
            
            # Integrate restaurants into daily activities
            for day_index, day in enumerate(daily_activities):
                day_number = day.get("day", day_index + 1)
                existing_activities = day.get("activities", [])
                
                # Find meal gaps in the schedule
                meal_times = {
                    "breakfast": ("07:00", "10:30"),
                    "lunch": ("11:30", "14:30"),
                    "dinner": ("18:00", "21:30")
                }
                
                scheduled_meals = set()
                for activity in existing_activities:
                    time = activity.get("time", "").lower()
                    if any(meal in time.lower() for meal in ["breakfast", "lunch", "dinner"]):
                        scheduled_meals.add(next(meal for meal in ["breakfast", "lunch", "dinner"] if meal in time.lower()))
                
                # For each unscheduled meal time, suggest a restaurant
                for meal, (start_time, end_time) in meal_times.items():
                    if meal not in scheduled_meals:
                        suitable_restaurants = [
                            r for r in restaurants 
                            if meal in r.get("best_time", "").lower()
                        ]
                        
                        if suitable_restaurants:
                            restaurant = suitable_restaurants[0]
                            restaurants.remove(restaurant)
                            
                            # Get day of week for hours
                            date_str = state["vacation_details"]["dates"].split(" to ")[0]
                            day_of_week = datetime.strptime(date_str, "%m-%d-%Y").strftime("%A").lower()
                            
                            meal_activity = {
                                "time": meal.title(),
                                "activity": f"{restaurant['name']} ({restaurant['cuisine']})",
                                "description": f"Signature dishes: {', '.join(restaurant['signature_dishes'][:2])}",
                                "notes": "\n".join([
                                    f"📞 {restaurant['phone']} | 👔 {restaurant['dress_code']}",
                                    f"📍 {restaurant['address']}",
                                    f"⏰ {restaurant['hours'][day_of_week]}",
                                    f"💡 {restaurant['reservation_notes']}"
                                ]),
                                "estimated_cost": restaurant['price_range']
                            }
                            existing_activities.append(meal_activity)
                
                # Sort activities by time
                day["activities"] = sorted(
                    existing_activities,
                    key=lambda x: meal_times.get(x.get("time", "").lower(), ("00:00", "00:00"))[0]
                )
            
            # Update itinerary
            state["itinerary"]["daily_activities"] = daily_activities
            
            # Store remaining suggestions
            state["restaurant_bookings"] = {
                "suggested_restaurants": restaurants,
                "notes": "Restaurants have been integrated into your daily itinerary. Additional suggestions are available if needed."
            }
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse restaurant suggestions: {e}")
            state["restaurant_bookings"] = {
                "error": "Failed to process restaurant suggestions",
                "details": str(e)
            }
        
        # Always complete the step to avoid recursion
        state["step_status"]["book_restaurants"] = "completed"
        state["current_step"] = "end"
        
    except Exception as e:
        print(f"Error in book_restaurants: {e}")
        state["step_status"]["book_restaurants"] = "error"
        state["current_step"] = "end"
        
    return state

def end_state(state: VacationState) -> VacationState:
    """Final state processing."""
    state["current_step"] = "completed"
    return state

# Create the graph
workflow = StateGraph(VacationState)

# Add our nodes
workflow.add_node("analyze", analyze_vacation_request)
workflow.add_node("plan_itinerary", plan_itinerary)
workflow.add_node("book_restaurants", book_restaurants)
workflow.add_node("end", end_state)

# Add our edges
workflow.add_edge("analyze", "plan_itinerary")
workflow.add_edge("plan_itinerary", "book_restaurants")
workflow.add_edge("book_restaurants", "end")

# Set up the entry point
workflow.set_entry_point("analyze")

# Compile the graph
app = workflow.compile()

def plan_vacation(request: str) -> Dict:
    """Process a vacation planning request."""
    initial_state = {
        "messages": [HumanMessage(content=request)],
        "vacation_details": {},
        "itinerary": {},
        "restaurant_bookings": [],
        "current_step": "analyze",
        "step_status": {},
        "errors": []
    }
    result = app.invoke(initial_state)
    
    # Convert to regular dict and clean up internal state
    output = {
        "vacation_details": result["vacation_details"],
        "itinerary": result["itinerary"],
        "restaurant_bookings": result["restaurant_bookings"],
        "errors": result["errors"]
    }
    return output

if __name__ == "__main__":
    # Example usage
    vacation_request = """
    I want to plan a relaxing beach vacation:
    - Dates: December 20-27, 2024
    - Type: Beach resort, luxury
    - Vibe: Peaceful and romantic
    - Budget: $8,000 total
    - Preference: Somewhere in the Caribbean
    """
    result = plan_vacation(vacation_request)
    
    print("\nVacation Planning Results:")
    print("=========================")
    print("\nVacation Details:")
    print(json.dumps(result["vacation_details"], indent=2))
    print("\nItinerary:")
    print(json.dumps(result["itinerary"], indent=2))
    print("\nRestaurant Bookings:")
    print(json.dumps(result["restaurant_bookings"], indent=2))
