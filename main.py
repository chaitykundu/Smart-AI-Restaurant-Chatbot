from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Request model for user inputs
class UserRequest(BaseModel):
    location: str
    cuisine: str
    price_range: str

# Mock function to simulate restaurant recommendations based on user input
def get_restaurant_recommendations(location, cuisine, price_range):
    # Simulating the recommendation process
    # This can be replaced with actual logic, e.g., querying a database of restaurants
    return {
        "restaurant": "Pizza Palace",
        "address": "123 Pizza St, City",
        "discount": "10%",
        "offer": f"Enjoy {price_range} {cuisine} with a {discount} discount!"
    }

# Route to handle user requests
@app.post("/get_recommendations/")
async def get_recommendations(request: UserRequest):
    location = request.location
    cuisine = request.cuisine
    price_range = request.price_range
    
    recommendations = get_restaurant_recommendations(location, cuisine, price_range)
    return recommendations
