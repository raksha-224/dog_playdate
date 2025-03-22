from typing import List, Dict
import random


# Assuming a simplified function for calculating distance between two locations
def calculate_distance(lat1, lon1, lat2, lon2):
    # Simple Euclidean distance; for real applications, you'd use a proper geospatial library
    return ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5


def calculate_match_weight(user_to_match, user):
    weight = 0

    # Assuming 'user_to_match' and 'user' have 'dogs' as a list of dog objects
    for dog_to_match in user_to_match.dogs:
        for dog in user.dogs:
            # Access dog_size using dot notation (not dictionary-style)
            if dog_to_match.dog_size == dog.dog_size:
                weight += 1  # Increase weight based on a match

    # You can add other criteria for the weight calculation here
    return weight


# Rule-Based Matching (location and availability)
def rule_based_match(user_to_match, users_df):
    user_lat, user_lon = user_to_match.location
    available_users = []

    for idx, user in users_df.iterrows():
        lat, lon = user['location']
        distance = calculate_distance(user_lat, user_lon, lat, lon)  # Calculate distance

        if distance < 50 and set(user_to_match.availability).intersection(set(user['availability'])):
            available_users.append(user)

    return available_users


# Phase 3 Matching (Additional Filtering)
def phase_3_matching(user_to_match, users_df):
    # Apply additional filtering logic
    refined_matches = []

    for idx, user in users_df.iterrows():
        if user_to_match.gender != user['gender']:  # Example filter: same gender preference
            continue
        refined_matches.append(user)

    return refined_matches


# Phase 4 Matching (Final Recommendations based on compatibility or other scores)
def phase_4_matching(user_to_match, users_df):
    # Final scoring and sorting based on compatibility or popularity
    final_matches = []

    for idx, user in users_df.iterrows():
        score = calculate_match_weight(user_to_match, user)  # Calculate final score
        final_matches.append((user, score))

    # Sort by score (higher score means better match)
    final_matches = sorted(final_matches, key=lambda x: x[1], reverse=True)

    return final_matches


# Weighted Matching (Factors like dogs, preferences, etc.)
def weighted_match(user_to_match, users_df):
    weighted_users = []

    for idx, user in users_df.iterrows():
        weight = calculate_match_weight(user_to_match, user)
        weighted_users.append((user, weight))

    # Sort based on the weight of the match
    weighted_users = sorted(weighted_users, key=lambda x: x[1], reverse=True)

    return weighted_users
