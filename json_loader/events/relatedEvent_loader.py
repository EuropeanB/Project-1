import json
import psycopg2
import os

# Database connection parameters
conn_params = {
    "dbname": "Project",  
    "user": "postgres",  
    "password": "3526384",  
    "host": "localhost" ,
    "port": "3526"
}

def get_target_match_ids(connection_params, competition_ids, season_ids):
    """Query the database for match IDs belonging to the target competition and season IDs."""
    target_match_ids = set()
    query = """
    SELECT match_id FROM matches 
    WHERE competition_id = %s AND season_id = %s
    """
    with psycopg2.connect(**connection_params) as conn:
        with conn.cursor() as cur:
            for comp_id in competition_ids:
                for season_id in season_ids:
                    cur.execute(query, (comp_id, season_id))
                    target_match_ids.update(str(match_id) for (match_id,) in cur.fetchall())
    return target_match_ids

target_match_ids = get_target_match_ids(conn_params, {'11', '2'}, {'4', '42', '90', '44'})

def load_json_files(directory, target_match_ids):
    """Load cards data from JSON files in the specified directory that are in the target match IDs."""
    for filename in os.listdir(directory):
        match_id = os.path.splitext(filename)[0]  # Get the match ID from filename
        if match_id in target_match_ids:
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
                for event in data:
                    if 'related_events' in event:
                        for related_event_id in event['related_events']:
                            yield {
                                'event_id': event["id"],  
                                'related_event_id': related_event_id
                            }

def insert_json_data(json_data_generator, connection_params):
    """Insert event data into the database."""
    insert_query = """
    INSERT INTO relatedEvents (
        event_id, related_event_id
    ) VALUES (
        %s, %s
    )

    """
    with psycopg2.connect(**connection_params) as conn:
        with conn.cursor() as cur:
            for item in json_data_generator:
                cur.execute(insert_query, (
                    item['event_id'], item['related_event_id']
                ))
        conn.commit()

# Directory containing JSON files
directory_path = 'D:\\Carleton university\\2024W\\COMP 3005\\Project\\data\\data\\events'

# Load JSON data
json_data_generator = load_json_files(directory_path, target_match_ids)

# Insert the JSON data into the database
insert_json_data(json_data_generator, conn_params)