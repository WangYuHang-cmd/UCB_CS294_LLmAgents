from typing import Dict, List
from autogen import ConversableAgent
import sys
import os
from autogen import register_function

# Constants for scoring
SCORE_KEYWORDS = {
    1: ["awful", "horrible", "disgusting"],
    2: ["bad", "unpleasant", "offensive"],
    3: ["average", "uninspiring", "forgettable"],
    4: ["good", "enjoyable", "satisfying"],
    5: ["awesome", "incredible", "amazing"]
}

# Data processing functions
def normalize(name: str) -> str:
    """
    Normalizes restaurant name by converting to lowercase, replacing punctuation with spaces,
    and removing extra spaces.
    Args:
    
        name (str): Restaurant name to normalize
        
    Returns:
        str: Normalized restaurant name
    """
    return (name.lower()
            .replace('-', ' ')
            .replace('.', ' ')
            .replace('  ', ' ')
            .strip())

def fetch_restaurant_data(restaurant_name: str) -> Dict[str, List[str]]:
    """
    Fetches reviews for a specific restaurant from the data file.
    
    Args:
        restaurant_name (str): Name of the restaurant to search for
        
    Returns:
        Dict[str, List[str]]: Dictionary with restaurant name as key and list of reviews as value
    """
    restaurant_data = {}
    reviews = []
    actual_name = None
    
    # Normalize the restaurant name
    restaurant_name_normalized = normalize(restaurant_name)
    
    try:
        with open('restaurant-data.txt', 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            if not line.strip():
                continue
            
            # Normalize the line using the same function
            line_normalized = normalize(line)
            
            if line_normalized.startswith(restaurant_name_normalized):
                actual_name = line.split('.')[0].strip()
                reviews.append(line.strip())
        
        if actual_name and reviews:
            restaurant_data[actual_name] = reviews
                
        return restaurant_data
    except FileNotFoundError:
        print("Error: restaurant-data.txt not found")
        return {}

def calculate_overall_score(restaurant_name: str, food_scores: List[int], customer_service_scores: List[int]) -> Dict[str, str]:
    """
    Calculates overall restaurant score using geometric mean formula.
    
    Args:
        restaurant_name (str): Name of the restaurant
        food_scores (List[int]): List of food quality scores (1-5)
        customer_service_scores (List[int]): List of service quality scores (1-5)
        
    Returns:
        Dict[str, float]: Dictionary with restaurant name and calculated score
    """
    N = len(food_scores)
    if N != len(customer_service_scores) or N == 0:
        raise ValueError("Food scores and customer service scores must have the same non-zero length")
    
    total = sum(
        ((f**2 * s)**0.5) * (1 / (N * (125**0.5))) * 10
        for f, s in zip(food_scores, customer_service_scores)
    )
    
    formatted_score = "{:.3f}".format(total)
    return {restaurant_name: formatted_score}

def get_data_fetch_agent_prompt(restaurant_query: str) -> str:
    return f"""You are a data fetch agent responsible for extracting restaurant names from user queries and fetching their reviews.
    
    Your task:
    1. Analyze the user query: "{restaurant_query}"
    2. Extract the restaurant name from the query
    3. Call the fetch_restaurant_data function with the extracted name
    """

def get_review_analyzer_prompt() -> str:
    keywords_str = "\n".join(
        f"        - {score}/5: {', '.join(words)}"
        for score, words in SCORE_KEYWORDS.items()
    )
    
    return f"""You are a review analyzer agent. Your task is to analyze restaurant reviews and extract scores.
    
    For each review:
    1. Find exactly one keyword for food quality and one for service quality
    2. Map keywords to scores using this exact mapping:
        Food/Service Score Mapping:
    
    {keywords_str}
    
    Output format must be exactly:
    food_scores = [score1, score2, ...]
    customer_service_scores = [score1, score2, ...]"""

def get_scoring_agent_prompt() -> str:
    return """You are a scoring agent. Your task is to take the food scores and customer service scores from the previous conversation and calculate the final rating.

    Steps:
    1. Extract the restaurant name from the data fetch result
    2. Get the food_scores and customer_service_scores lists from the analyzer
    3. Call calculate_overall_score with these exact parameters
    
    """

def create_agent(name: str, system_message: str, llm_config: dict) -> ConversableAgent:
    """Helper function to create agents with consistent configuration."""
    return ConversableAgent(
        name=name,
        system_message=system_message,
        llm_config=llm_config
    )

def main(user_query: str):
    """
    Main function to process restaurant queries and return ratings.
    
    Args:
        user_query (str): User's query about a restaurant
        
    Returns:
        The result of the agent conversation chain
    """
    llm_config = {"config_list": [{"model": "gpt-4o", "api_key": os.environ.get("OPENAI_API_KEY")}]}
    
    # Create the entrypoint agent
    entrypoint_agent = create_agent(
        "entrypoint_agent",
        """You are the supervisor agent coordinating the restaurant review analysis process.
        Follow these steps exactly:
        1. First, ask the data fetch agent to get restaurant reviews using fetch_restaurant_data
        2. Once you have the reviews, send them to the review analyzer to extract scores
        3. After getting the scores from the analyzer, ask the scoring agent to calculate the final rating
        """,
        llm_config
    )
    
    # Create specialized agents
    agents = {
        "data_fetch": create_agent(
            "data_fetch_agent", 
            get_data_fetch_agent_prompt(user_query), 
            llm_config
        ),
        "analyzer": create_agent(
            "review_analyzer_agent", 
            get_review_analyzer_prompt(), 
            llm_config
        ),
        "scorer": create_agent(
            "scoring_agent", 
            get_scoring_agent_prompt(), 
            llm_config
        )
    }
    
    # Register functions for all necessary agents
    # Data fetch related
    register_function(
        fetch_restaurant_data,
        caller=entrypoint_agent,  
        executor=agents['data_fetch'], 
        name="fetch_restaurant_data", 
        description="Fetches the reviews for a specific restaurant."
    )
    
    # Scoring related
    register_function(
        calculate_overall_score,
        caller=entrypoint_agent,  
        executor=agents['scorer'], 
        name="calculate_overall_score", 
        description="Calculates the overall score for a restaurant."
    )
    
    # Update chat sequence with more explicit messages
    chat_sequence = [
        {
            "recipient": agents["data_fetch"],
            "message": f"Find reviews for this query: {user_query}",
            "summary_method": "last_msg",
            "max_turns": 2
        },
        {
            "recipient": agents["analyzer"],
            "message": "Here are the reviews from the data fetch agent. Please analyze them and extract food and service scores. For each review, find the food quality keyword and service quality keyword, then map them to scores 1-5 according to the scoring rules.",
            "summary_method": "last_msg",
            "max_turns": 1
        },
        {
            "recipient": agents["scorer"],
            "message": "Using the food_scores and customer_service_scores from the analyzer, please calculate the final restaurant rating using calculate_overall_score.",
            "summary_method": "last_msg",
            "max_turns": 2
        }
    ]
    
    result = entrypoint_agent.initiate_chats(chat_sequence)
    print(result)
    return result

if __name__ == "__main__":
    assert len(sys.argv) > 1, "Please ensure you include a query for some restaurant when executing main."
    main(sys.argv[1])
