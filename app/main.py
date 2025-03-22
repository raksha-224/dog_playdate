import random
from pydantic import BaseModel
from typing import List, Tuple, Dict, Optional
from fastapi import FastAPI

# Initialize FastAPI app
app = FastAPI(title="Dog Playdate Matcher API", 
              description="API for matching dog owners for playdates based on location, availability, and dog compatibility")

# Define DogRequest model
class DogRequest(BaseModel):
    dog_name: str
    dog_breed: str
    dog_age: str
    dog_size: str
    dog_size_in_lb: int
    dog_energy: str
    dog_friendly: str
    shots_up_to_date: bool

# Define UserRequest model
class UserRequest(BaseModel):
    id: str
    name: str
    gender: str
    relationship_status: str
    location: Tuple[float, float]  # (latitude, longitude)
    availability: List[str]
    dogs: List[DogRequest]

# Define response models for better API documentation
class DogCompatibilityDetail(BaseModel):
    dog1: str
    dog2: str
    score: int
    notes: List[str]

class MatchRecommendation(BaseModel):
    rank: int
    user: Dict
    distance: float
    common_times: List[str]
    compatibility_score: int
    dog_compatibility: List[DogCompatibilityDetail]

class MatchResponse(BaseModel):
    matches: List[MatchRecommendation]

# Helper function to generate random dog data
def generate_random_dog():
    dog_names = ["Buddy", "Max", "Bella", "Lucy", "Charlie", "Cooper", "Luna", "Bailey", "Daisy", "Sadie"]
    breeds = ["Labrador", "Beagle", "German Shepherd", "Poodle", "Bulldog", "Golden Retriever", "Chihuahua", "Pug", "Husky", "Boxer"]
    sizes = ["Small", "Medium", "Large"]
    energy_levels = ["Low", "Medium", "High"]
    friendliness = ["Friendly", "Neutral", "Aggressive"]
    
    dog_name = random.choice(dog_names)
    dog_breed = random.choice(breeds)
    dog_age = f"{random.randint(1, 10)} years {random.randint(1, 12)} months"
    dog_size = random.choice(sizes)
    dog_size_in_lb = random.randint(10, 120)
    dog_energy = random.choice(energy_levels)
    dog_friendly = random.choice(friendliness)
    shots_up_to_date = random.choice([True, False])
    
    return DogRequest(
        dog_name=dog_name,
        dog_breed=dog_breed,
        dog_age=dog_age,
        dog_size=dog_size,
        dog_size_in_lb=dog_size_in_lb,
        dog_energy=dog_energy,
        dog_friendly=dog_friendly,
        shots_up_to_date=shots_up_to_date
    )

# Helper function to generate random user data
def generate_random_user(user_id: str):
    names = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Henry", "Isabel", "Jack"]
    genders = ["Male", "Female", "Other"]
    relationship_status = ["Single", "In a Relationship", "Married"]
    availabilities = [["Morning", "Afternoon"], ["Afternoon", "Evening"], ["Morning", "Evening"], ["Morning", "Afternoon", "Evening"]]
    
    name = random.choice(names)
    gender = random.choice(genders)
    relationship = random.choice(relationship_status)
    location = (random.uniform(-90, 90), random.uniform(-180, 180))  # Random lat, long
    availability = random.choice(availabilities)
    dogs = [generate_random_dog() for _ in range(random.randint(1, 3))]  # Each user can have 1 to 3 dogs
    
    return UserRequest(
        id=user_id,
        name=name,
        gender=gender,
        relationship_status=relationship,
        location=location,
        availability=availability,
        dogs=dogs
    )

# Function to generate random data for users
def generate_random_data(num_users=10):
    users_data = []
    for i in range(num_users):
        users_data.append(generate_random_user(str(i+1)))
    return users_data

# Calculate the distance between two locations using Haversine formula (more accurate for geographic coordinates)
def calculate_distance(lat1, lon1, lat2, lon2):
    from math import radians, sin, cos, sqrt, atan2
    
    # Convert latitude and longitude from degrees to radians
    lat1, lon1 = radians(lat1), radians(lon1)
    lat2, lon2 = radians(lat2), radians(lon2)
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    # Radius of Earth in kilometers
    radius = 6371
    
    # Calculate distance
    distance = radius * c
    
    return distance

# Phase 1: Location-Based Matching
def phase_1_location_matching(user_to_match, users_data, max_distance=50.0):
    """
    Filter users based on proximity (within max_distance)
    """
    user_lat, user_lon = user_to_match.location
    location_matches = []
    
    for user in users_data:
        if user.id == user_to_match.id:  # Skip matching with self
            continue
            
        lat, lon = user.location
        distance = calculate_distance(user_lat, user_lon, lat, lon)
        
        if distance <= max_distance:
            location_matches.append((user, distance))
    
    # Sort by distance
    location_matches.sort(key=lambda x: x[1])
    
    return location_matches

# Phase 2: Availability Matching
def phase_2_availability_matching(user_to_match, location_matches):
    """
    Filter users based on matching availability
    """
    availability_matches = []
    
    for user, distance in location_matches:
        common_availability = set(user_to_match.availability).intersection(set(user.availability))
        
        if common_availability:
            availability_matches.append((user, distance, list(common_availability)))
    
    return availability_matches

# Phase 3: Dog Compatibility Matching
def phase_3_dog_compatibility(user_to_match, availability_matches):
    """
    Match based on dog compatibility factors
    """
    compatibility_matches = []
    
    for user, distance, common_availability in availability_matches:
        compatibility_score = 0
        compatibility_details = []
        
        # Check for shots up to date
        all_shots_up_to_date = all(dog.shots_up_to_date for dog in user_to_match.dogs) and all(dog.shots_up_to_date for dog in user.dogs)
        if not all_shots_up_to_date:
            # Skip users with dogs that don't have shots up to date
            continue
            
        # For each dog pair, calculate compatibility
        for dog1 in user_to_match.dogs:
            for dog2 in user.dogs:
                dog_score = 0
                dog_compatibility_notes = []
                
                # Size compatibility
                if dog1.dog_size == dog2.dog_size:
                    dog_score += 3
                    dog_compatibility_notes.append(f"Same size ({dog1.dog_size})")
                elif (dog1.dog_size == "Medium" and dog2.dog_size in ["Small", "Large"]) or \
                     (dog2.dog_size == "Medium" and dog1.dog_size in ["Small", "Large"]):
                    dog_score += 1
                    dog_compatibility_notes.append("Compatible sizes")
                
                # Energy level compatibility
                if dog1.dog_energy == dog2.dog_energy:
                    dog_score += 3
                    dog_compatibility_notes.append(f"Matching energy levels ({dog1.dog_energy})")
                elif (dog1.dog_energy == "Medium" or dog2.dog_energy == "Medium"):
                    dog_score += 1
                    dog_compatibility_notes.append("Adaptable energy levels")
                
                # Friendliness compatibility
                if dog1.dog_friendly == "Friendly" and dog2.dog_friendly == "Friendly":
                    dog_score += 3
                    dog_compatibility_notes.append("Both dogs are friendly")
                elif dog1.dog_friendly != "Aggressive" and dog2.dog_friendly != "Aggressive":
                    dog_score += 1
                    dog_compatibility_notes.append("Neither dog is aggressive")
                else:
                    # If either dog is aggressive, reduce compatibility
                    dog_score -= 2
                    dog_compatibility_notes.append("Potential aggression issues")
                
                # Breed compatibility (optional, just for fun)
                if dog1.dog_breed == dog2.dog_breed:
                    dog_score += 1
                    dog_compatibility_notes.append(f"Same breed ({dog1.dog_breed})")
                
                compatibility_details.append({
                    "dog1": dog1.dog_name,
                    "dog2": dog2.dog_name,
                    "score": dog_score,
                    "notes": dog_compatibility_notes
                })
                
                compatibility_score += dog_score
        
        # Only include matches with positive compatibility scores
        if compatibility_score > 0:
            compatibility_matches.append({
                "user": user,
                "distance": distance,
                "common_availability": common_availability,
                "compatibility_score": compatibility_score,
                "compatibility_details": compatibility_details
            })
    
    # Sort by compatibility score (highest first)
    compatibility_matches.sort(key=lambda x: x["compatibility_score"], reverse=True)
    
    return compatibility_matches

# Phase 4: Final Recommendations
def generate_final_recommendations(user_to_match, users_data, max_matches=5):
    """
    Generate final recommendations by running all phases
    """
    # Phase 1: Location-based matching
    location_matches = phase_1_location_matching(user_to_match, users_data)
    
    # Phase 2: Availability matching
    availability_matches = phase_2_availability_matching(user_to_match, location_matches)
    
    # Phase 3: Dog compatibility matching
    compatibility_matches = phase_3_dog_compatibility(user_to_match, availability_matches)
    
    # Prepare final recommendations
    final_recommendations = []
    
    for i, match in enumerate(compatibility_matches[:max_matches]):  # Top matches
        user = match["user"]
        
        recommendation = {
            "rank": i + 1,
            "user": {
                "id": user.id,
                "name": user.name,
                "dogs": [dog.dog_name for dog in user.dogs]
            },
            "distance": match["distance"],
            "common_times": match["common_availability"],
            "compatibility_score": match["compatibility_score"],
            "dog_compatibility": match["compatibility_details"]
        }
        
        final_recommendations.append(recommendation)
    
    return final_recommendations

# Define API endpoints
@app.post("/generate_users", response_model=Dict[str, List[UserRequest]])
def generate_users(num_users: int = 10):
    """
    Generate a specified number of random user profiles for testing
    """
    users = generate_random_data(num_users)
    return {"users": users}

@app.post("/find_matches", response_model=MatchResponse)
def find_matches(user_to_match: UserRequest, users_data: List[UserRequest] = None, max_matches: int = 5, max_distance: float = 50.0):
    """
    Find dog playdate matches for the specified user
    
    - **user_to_match**: User profile to find matches for
    - **users_data**: List of other user profiles to match against (if None, generates random users)
    - **max_matches**: Maximum number of matches to return
    - **max_distance**: Maximum distance (in km) to consider for matches
    """
    if users_data is None:
        # Generate 20 random users if none provided
        users_data = generate_random_data(20)
        
    # Generate recommendations
    final_recommendations = generate_final_recommendations(user_to_match, users_data, max_matches)
    
    return {"matches": final_recommendations}

# Example test code (only runs when script is executed directly)
if __name__ == "__main__":
    # Generate random data
    users = generate_random_data(20)
    
    # Show basic info about generated users
    print("=== Generated Users ===")
    for i, user in enumerate(users):
        print(f"User {i+1}: {user.name} with {len(user.dogs)} dogs")
        print(f"  Location: {user.location}")
        print(f"  Availability: {', '.join(user.availability)}")
        print(f"  Dogs: {', '.join([f'{dog.dog_name} ({dog.dog_size}, {dog.dog_energy}, {dog.dog_friendly})' for dog in user.dogs])}")
        print()
    
    # Select the first user as the one to match
    user_to_match = users[0]
    
    # Generate recommendations
    recommendations = generate_final_recommendations(user_to_match, users)
    
    print("\n=== Summary of Recommendations ===")
    if recommendations:
        for rec in recommendations:
            print(f"#{rec['rank']}: {rec['user']['name']} (Score: {rec['compatibility_score']})")
    else:
        print("No compatible matches found.")
