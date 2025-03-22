import random
from pydantic import BaseModel
from typing import List, Tuple

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

# Helper function to generate random dog data
def generate_random_dog():
    dog_names = ["Buddy", "Max", "Bella", "Lucy", "Charlie"]
    breeds = ["Labrador", "Beagle", "German Shepherd", "Poodle", "Bulldog"]
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
    names = ["Alice", "Bob", "Charlie", "David", "Eve"]
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
