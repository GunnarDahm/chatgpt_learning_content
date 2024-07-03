
from openai import OpenAI
from pprint import pprint
from datetime import datetime
import json

# reading 
with open('creds.json') as json_data:
    d = json.load(json_data)
    json_data.close()

# Set up your OpenAI and Notion API keys
client = OpenAI(api_key=d['open_api_creds'])


#template_id = "your_template_id"

def get_summary(master_topic, topic):
    # Adds additional context to sub-topics to keep gpt on track 
    if master_topic == None:
        appendix= ''
    else:
        appendix= f'as it relates to {master_topic}'

    prompt = f'''Please provide a brief summary of roughly 200 to 300 words of the following topic: {topic} {appendix}. Please ensure the summary of the topic is one singular paragraph. Please ensure the summary is strictly less than 2,000 characters. Additionally, please respond using the following format:  
[Topic]: [Summary of Topic] . '''
    
    response = client.with_options(max_retries=5).chat.completions.create(
        model="gpt-3.5-turbo",
        messages = [{"role":"user",
                        "content":prompt}],
        max_tokens=1024,
        temperature=0.2
    )

    print(response['choices'][0]['message']['content'].strip())
    return response['choices'][0]['message']['content'].strip()

def get_subtopics(master_topic, topic):

    # Takes a master topic 
    if master_topic == None:
        appendix= ''
    else:
        appendix= f'as it relates to {master_topic}'


    prompt = f'''Please provide a list of between 5 to 10 related subtopics for the topic: {topic} {appendix}. Enumerate the list with numbers. Subtopics should be described in 15 words or less. Additionally, please respond using the following format:  
    1. [[Title of Subtopic 1, less than 15 words]]
    2. [[Title of Subtopic 2, less than 15 words]]
    3. [[Title of Subtopic 3, less than 15 words]]
    4. [[Title of Subtopic 4, less than 15 words]]
    5. [[Title of Subtopic 4, less than 15 words]]...'''

    response = client.with_options(max_retries=5).chat.completions.create(
        model="gpt-3.5-turbo",
        messages = [{"role":"user",
                        "content":prompt}],
        max_tokens=1024,
        temperature=0.2
    )

    print(response['choices'][0]['message']['content'].strip())
    return response['choices'][0]['message']['content'].strip()


def create_markdown_page(title, summary, subtopics, depth, parent_link=None):
    # Creates the markdown file with a parent link (if applicable), summary, and links to subtopics

    if parent_link:
        link = f'Parent: [[{parent_link}]]'

    else:
        link=''

    with open(f"content/{title}.md", "w") as file:
        file.write(f'''
            ---
            tags:
            - "#AI-Generated"
            - "#Notes"
            Area: Learning
            Depth: {depth}
            ---
            
            {link}

            ### Summary              
            {summary}

            ### Subtopics
            {subtopics}

        ''')

    file.close()

    return title

def create_course_structure(master_topic, topic, depth, current_depth=0, parent_page_id=None):
    # For purposes of accuracy, set master_topic and topic as the same value 
    if current_depth > depth:
        return

    # generating the topics and subtopics with attempt handling for gpt timeouts

    summary = get_summary(master_topic, topic)
    subtopics = get_subtopics(master_topic, topic).split("\n")

    # creating the current page
    new_page_name = create_markdown_page(title=topic, 
                                         summary=summary, 
                                         subtopics=subtopics, 
                                         depth=current_depth, 
                                         parent_link=parent_page_id)

    # recursion for each subtopic and calling this function
    for subtopic in subtopics:
        if subtopic in ['\n','Subtopics:','']:
            # skipping the header
            pass
        else:
            create_course_structure(master_topic, subtopic.strip(), depth, current_depth + 1, new_page_name)
            

# Pass your topic and desired depth here
master_topic = "Early Roman History"
topic = 'Early Roman History'
depth = 1

create_course_structure(master_topic=None, topic=topic, depth=depth)
#create_markdown_page(topic, 'test', 'subtopics', depth)