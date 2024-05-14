
import openai
import os
from pprint import pprint
import requests
from datetime import datetime

# Set up your OpenAI and Notion API keys
openai.api_key = ""


#template_id = "your_template_id"

def get_summary(master_topic, topic, master = False):
    # Takes a master topic 
    if master == True:
        appendix= ''
    else:
        appendix= f'as it relates to {master_topic}'

    prompt = f'''Please provide a brief summary of roughly 200 to 300 words of the following topic: {topic} {appendix}. Please ensure the summary of the topic is one singular paragraph. Please ensure the summary is strictly less than 2,000 characters. Additionally, please respond using the following format:  
[Topic]: [Summary of Topic] . '''
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages = [{"role":"user",
                        "content":prompt}],
        max_tokens=1024,
        temperature=0.3
    )

    print(response['choices'][0]['message']['content'].strip())
    return response['choices'][0]['message']['content'].strip()

def get_subtopics(master_topic, topic):
    prompt = f'''Please provide a list of 5 to 10 related subtopics for the topic: {topic} as it relates to {master_topic}. Enumerate the list with numbers. Subtopics should be described in 15 words or less. Additionally, please respond using the following format:  
    1. [Topic]: [Title of Subtopic 1, less than 10 words]
    2. [Topic]: [Title of Subtopic 2, less than 10 words]
    3. [Topic]: [Title of Subtopic 3, less than 10 words]
    4. [Topic]: [Title of Subtopic 4, less than 10 words]
    5. [Topic]: [Title of Subtopic 4, less than 10 words]'''
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages = [{"role":"user",
                        "content":prompt}],
        max_tokens=1024,
        temperature=0.3
    )

    print(response['choices'][0]['message']['content'].strip())
    return response['choices'][0]['message']['content'].strip()


def create_obsidian_page(database_id, title, summary, depth, parent_page_id=None):
    new_page = {
        "Name": {"title": [{"text": {"content": f"{title}"}}]},
        "Summary": {"rich_text": [{"text": {"content": f"{summary}"}}]},
        "Depth":{"number":depth},
        "Tag": {"multi_select": [{"name": 'AI Content'}]}
    }
    if parent_page_id:
        new_page["Roll Up"] = {"relation": [{"id": parent_page_id}]}

    created_page = notion.pages.create(parent={"database_id": database_id}, properties=new_page)

    return created_page["id"]

def create_course_structure(master_topic, topic, depth, current_depth=0, parent_page_id=None):
    # For purposes of accuracy, set master_topic and topic as the same value 
    if current_depth > depth:
        return

    attempts = 0
    for n in range(0,4):
        if attempts <3:
            # adding multiple attempts as the openAi often throws rate limit errors
            try:
                summary = get_summary(master_topic, topic)
                subtopics = get_subtopics(master_topic, topic).split("\n")
                break

            except openai.error.RateLimitError:
                print(f'Attempt {attempts} failed.')
                attempts=attempts+1

            except Client.HTTPStatusError:
                print(f'Attempt {attempts} failed.')
                attempts=attempts+1

            except openai.error.APIError:
                print(f'Attempt {attempts} failed.')
                attempts=attempts+1

        else:
            raise NameError

    new_page_id = create_notion_page(course_database_id, topic, summary, current_depth, parent_page_id)

    for subtopic in subtopics:
        if subtopic in ['\n','Subtopics:','']:
            # skipping the header
            pass
        else:
            create_course_structure(master_topic, subtopic.strip(), depth, current_depth + 1, new_page_id)
            

# Pass your topic and desired depth here
master_topic = "Concepts and Skills of a Salesforce Certified Administrator"
topic = 'AppExchange and Integration'
depth = 1

create_course_structure(master_topic=master_topic, topic=topic, depth=depth)