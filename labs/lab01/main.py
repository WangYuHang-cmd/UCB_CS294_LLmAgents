from typing import Dict, List
import math
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
def format_name(name: str) -> str:
    """
    Args:
        name (str): The formated name of the restaurant
        
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
    Return a dict including all the restaurants's reviews

    Args:
        restaurant_name (str)
        
    Returns:
        Dict[str, List[str]]: The reviews dict
    """
    restaurant_name_formatted = format_name(restaurant_name)
    restaurant_reviews_dict = {}
    review_list = []
    try:
        with open('restaurant-data.txt', 'r') as file:
            lines = file.readlines()
        for line in lines:
            if not line.strip():
                continue
            line_formated = format_name(line)
            if line_formated.startswith(restaurant_name_formatted):
                restaurant_name_in_text = line.split('.')[0].strip()
                review_list.append(line.strip())
        if restaurant_name and review_list:
            restaurant_reviews_dict[restaurant_name_in_text] = review_list
        return restaurant_reviews_dict
    except FileNotFoundError:
        print('Error in reading the file')


def calculate_overall_score(restaurant_name: str, food_scores: List[int], customer_service_scores: List[int]) -> Dict[str, float]:
    """
    Return a dict including all the restaurants's reviews

    Args:
        restaurant_name (str)

        food_scores (List[int])

        customer_service_scores (List[int])
        
    Returns:
        Dict[str, float]: The dict of score
    """

    N = len(food_scores)

    if N == 0 or N != len(customer_service_scores):
        print("List size is wrong for customer score and food score.")
        return -1
    
    score = 0
    for i in range(0, N):
        score += math.sqrt(food_scores[i]**2 * customer_service_scores[i]) * 1 / (N * math.sqrt(125)) * 10
    return {restaurant_name: "{:.3f}".format(score)}

def get_agent(role: str, prompt: str, llm_config: dict) -> ConversableAgent:
    return ConversableAgent(
        name=role,
        system_message=prompt,
        llm_config=llm_config
    )

def get_data_fetch_agent_prompt(restaurant_query: str) -> str:
    """
    Return a dict including all the restaurants's reviews

    Args:
        restaurant_query (str)
        
    Returns:
        Prompt (str): The prompt to solve restaurant_query
    """
    return f"""You are a data fetch agent for getting restautant name from user quires and fetching all their reviews.

You need to do the following steps:
    step_1. Understanding user query {restaurant_query} and analysis it.
    step_2. Extract the restaurant name from the query: <restaurant_name>
    step_3. Call the fetch_restaurant_data function with the parameter <restaurant_name> you get in step_2.
"""

def get_reivew_analysis_agent_prompt() -> str:
    score_map = ""

    for key in SCORE_KEYWORDS.keys():
        score_map += f"{key}: "
        for word in SCORE_KEYWORDS[key]:
            score_map += f"{word}, "
        score_map += "\n"

    return f"""You are a restaurant review analyzer agent. Your task is to analyze restaurant reviews and extract scores.

You need to do the following steps:
    step_1. Find the exact keywords for food quality and the exact keywords for service quality.
    step_2. Choose the best score corresponding to the keywords you choose in step_1 for food quality and service quality following the score map below:
        {score_map}
    
    The output format should strictly adhere to the following:
    - food_scores = [score1, score2, ...]
    - customer_service_scores = [score1, score2, ...]"""

def get_scoring_agent_prompt() -> str:
    return """You are a scoring agent for restaurant reviews. Your task is to take the food scores and customer service scores from the previous conversation and calculate the final composite score.

You need to do the following steps:
    step_1. Extract the restaurant name <restaurant_name> from the data fetch agent.
    step_2. Get the food scores <food_scores> and customer service scores <customer_service_scores> from the review analysis agent.
    step_3. Call the calculate_overall_score function with the parameter <restaurant_name>, <food_scores>, <customer_service_scores>.
"""

# Do not modify the signature of the "main" function.
def main(user_query: str):
    # example LLM config for the entrypoint agent
    llm_config = {"config_list": [{"model": "gpt-4o", "api_key": os.environ.get("OPENAI_API_KEY")}]}
    
    entrypoint_agent_system_message = f"""You are a manager Agent used to organise the scoring of restaurant reviews. 

Please follow these instructions in order.
    1. First, let the data fetch agent call the fetch_restaurant_data function to get the restaurant reviews.
    2. Send the reviews to the review analysis agent to extract the score of the restaurant
    3. Once you get the score from the review analysis agent, let the scoring agent to calculate the final rating
    
Make sure you're just a coordinator and don't add any extra actions.
    """
    
    # the main entrypoint/supervisor agent
    entrypoint_agent = ConversableAgent("entrypoint_agent", 
                                        system_message=entrypoint_agent_system_message, 
                                        llm_config=llm_config)
    # entrypoint_agent.register_for_llm(name="fetch_restaurant_data", description="Fetches the reviews for a specific restaurant.")(fetch_restaurant_data)
    # entrypoint_agent.register_for_execution(name="fetch_restaurant_data")(fetch_restaurant_data)

    # TODO
    agents = {
        "data_fetch_agent": get_agent(
            "data_fetch_agent",
            get_data_fetch_agent_prompt(user_query),
            llm_config,
        ),
        "review_analysis_agent": get_agent(
            "review_analysis_agent",
            get_reivew_analysis_agent_prompt(),
            llm_config,
        ),
        "scoring_agent": get_agent(
            "scoring_agent",
            get_scoring_agent_prompt(),
            llm_config,
        )
    }

    # def register_function(f: Callable[..., Any],
    #                   *,
    #                   caller: ConversableAgent,
    #                   executor: ConversableAgent,
    #                   name: Optional[str] = None,
    #                   description: str) -> None
    # register data_fetch_agent
    register_function(
        fetch_restaurant_data,
        caller=entrypoint_agent,
        executor=agents['data_fetch_agent'],
        name="fetch_restaurant_data",
        description="Fetches the reviews for a specific restaurant."
    )

    # register scoring_agent
    register_function(
        calculate_overall_score,
        caller=entrypoint_agent,
        executor=agents['scoring_agent'],
        name="calculate_overall_score",
        description="Calculate the overall score for the restaurant."
    )
    
    # TODO
    result = entrypoint_agent.initiate_chats([
        {
            "recipient": agents["data_fetch_agent"],
            "message": f"Find all the reviews for the following query: {user_query}",
            "summary_method": "last_msg",
            "max_turns": 2,
        },
        {
            "recipient": agents["review_analysis_agent"],
            "message": "Here are the reviews from the data fetch agent. Please analyze them and extract food and service scores. For each review, find the food quality keyword and service quality keyword, then map them to scores 1-5 according to the scoring map.",
            "summary_method": "last_msg",
            "max_turns": 1,
        },
        {
            "recipient": agents["scoring_agent"],
            "message": "Using the food_scores and customer_service_scores from the review analysis agent, please calculate the final restaurant score using calculate_overall_score.",
            "summary_method": "last_msg",
            "max_turns": 2
        },
    ])
    print(result)
    return result
    
# DO NOT modify this code below.
if __name__ == "__main__":
    assert len(sys.argv) > 1, "Please ensure you include a query for some restaurant when executing main."
    main(sys.argv[1])