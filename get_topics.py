import requests
import json
from pathlib import Path
from collections import defaultdict
import time
from datetime import datetime

def read_api_key():
    """Read API key from file."""
    with open('api_key.txt', 'r') as f:
        return f.read().strip()

def get_topics(query_term, size=10):
    """Fetch topics from Starscape API."""
    url = "https://starscape.infegy.com/api/query/topics"
    
    # Read API key
    api_key = read_api_key()
    
    # Prepare headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Prepare payload
    payload = {
        "dataset_id": "ds_gj4u3F40SLa",
        "timezone": "Etc/UTC",
        "query": {
            "op": "contains",
            "fields": ["title", "body"],
            "value": query_term
        },
        "topics": {
            "size": size,
            "types": ["topic"],
            "clustering_bias": 0.5
        }
    }
    
    print(f"Making API request for: {query_term}")
    start_time = time.time()
    
    # Make API request
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        elapsed_time = time.time() - start_time
        print(f"API request completed in {elapsed_time:.2f} seconds")
        return response.json()
    else:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

def consolidate_small_categories(data, threshold=0.05):
    """
    Consolidate small categories into an "Other" category.
    threshold: minimum proportion to keep as a separate category
    """
    # Calculate total value
    total_value = sum(item['value'] for item in data)
    
    # Separate main categories and small categories
    main_categories = []
    small_categories = []
    
    for item in data:
        proportion = item['value'] / total_value
        if proportion >= threshold:
            main_categories.append(item)
        else:
            small_categories.append(item)
    
    # If there are small categories, create an "Other" category
    if small_categories:
        other_value = sum(item['value'] for item in small_categories)
        other_category = {
            'name': 'Other',
            'value': other_value,
            'proportion': other_value / total_value,  # Calculate proportion for Other category
            'children': small_categories
        }
        main_categories.append(other_category)
    
    return main_categories

def process_topics_data(data):
    """Process the topics data into a hierarchical structure for visualization."""
    if not isinstance(data, dict):
        raise ValueError(f"Expected dictionary response, got {type(data)}")
    
    topics = data.get('topics', [])
    if not topics:
        raise ValueError("No topics found in the response")
    
    print(f"\nFound {len(topics)} top-level topics")
    
    # Create hierarchical structure with proportions
    hierarchical_data = build_hierarchical_structure(topics)
    
    # Debug: Print the final hierarchical structure
    print("\nFinal hierarchical structure:")
    print(json.dumps(hierarchical_data, indent=2))
    
    return hierarchical_data

def build_hierarchical_structure(top_level_topics):
    """
    Build a hierarchical structure by making sequential API calls for each top-level topic.
    """
    # Initialize the hierarchical structure
    hierarchy = {
        'name': 'Topics',
        'children': []
    }
    
    total_topics = len(top_level_topics)
    print(f"\nProcessing {total_topics} top-level topics...")
    
    # Process each top-level topic
    for i, topic in enumerate(top_level_topics, 1):
        relationships = topic.get('relationships', [])
        if not relationships:
            continue
            
        # Get the primary relationship (topic with itself)
        primary = relationships[0]
        topic_name = primary.get('label')
        topic_value = primary.get('cooccurrence', 0)
        
        print(f"\nProcessing topic {i}/{total_topics}: {topic_name}")
        
        # Create main topic data
        main_topic_data = {
            'name': topic_name,
            'value': topic_value,
            'children': []
        }
        
        # Get subtopics for this main topic
        print(f"Fetching subtopics for: {topic_name}")
        subtopics_data = get_topics(topic_name)
        
        if subtopics_data and 'topics' in subtopics_data:
            subtopics = subtopics_data['topics']
            print(f"Found {len(subtopics)} subtopics for {topic_name}")
            
            # Process subtopics
            subtopic_items = []
            for subtopic in subtopics:
                subtopic_relationships = subtopic.get('relationships', [])
                if not subtopic_relationships:
                    continue
                    
                subtopic_primary = subtopic_relationships[0]
                subtopic_name = subtopic_primary.get('label')
                subtopic_value = subtopic_primary.get('cooccurrence', 0)
                
                # Skip if the subtopic is the same as the main topic
                if subtopic_name == topic_name:
                    continue
                
                subtopic_items.append({
                    'name': subtopic_name,
                    'value': subtopic_value
                })
            
            # Calculate proportions for subtopics
            if subtopic_items:
                total_subtopic_value = sum(item['value'] for item in subtopic_items)
                for item in subtopic_items:
                    item['proportion'] = item['value'] / total_subtopic_value if total_subtopic_value > 0 else 0
                
                consolidated_subtopics = consolidate_small_categories(subtopic_items, threshold=0.05)
                main_topic_data['children'] = consolidated_subtopics
            
            print(f"Added {len(main_topic_data['children'])} unique subtopics to {topic_name}")
        
        hierarchy['children'].append(main_topic_data)
        
        # Add a small delay to avoid rate limiting
        time.sleep(1)
    
    # Calculate proportions for main topics
    total_value = sum(group.get('value', 0) for group in hierarchy['children'])
    for group in hierarchy['children']:
        group['proportion'] = group.get('value', 0) / total_value if total_value > 0 else 0
    
    # Consolidate small main topics
    hierarchy['children'] = consolidate_small_categories(hierarchy['children'], threshold=0.05)
    
    # Recalculate proportions after consolidation
    total_value = sum(group.get('value', 0) for group in hierarchy['children'])
    for group in hierarchy['children']:
        group['proportion'] = group.get('value', 0) / total_value if total_value > 0 else 0
    
    return hierarchy

def main():
    # Example usage
    query_term = "recipe"  # You can change this to any search term
    size = 10  # Number of topics to retrieve
    
    try:
        start_time = time.time()
        print(f"Starting data collection at {datetime.now().strftime('%H:%M:%S')}")
        
        # Get top-level topics data
        print(f"\nFetching top-level topics for query: {query_term}")
        data = get_topics(query_term, size)
        
        # Process data into hierarchical structure
        print("\nProcessing topics data...")
        hierarchical_data = process_topics_data(data)
        
        # Save processed data to JSON file
        output_file = 'topics_data.json'
        with open(output_file, 'w') as f:
            json.dump(hierarchical_data, f, indent=2)
        
        total_time = time.time() - start_time
        print(f"\nSuccessfully processed topics data and saved to {output_file}")
        print(f"Total execution time: {total_time:.2f} seconds")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print("\nFull error traceback:")
        print(traceback.format_exc())

if __name__ == "__main__":
    main() 