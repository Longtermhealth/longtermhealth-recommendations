# rule_based_system/main_flask.py
import traceback

import requests
from flask import Flask, request, jsonify
from config import Config
from utils.typeform_api import get_responses, get_field_mapping, process_latest_response, get_last_name
from utils.clickup_api import create_clickup_task, upload_file_to_clickup
from utils.data_loader import load_routines, load_rules
from utils.data_processing import integrate_answers
from assessments.health_assessment import HealthAssessment
from scheduling.scheduler import generate_schedule, display_monthly_plan
import matplotlib.pyplot as plt
import numpy as np
import os
from bs4 import BeautifulSoup
from openai import OpenAI


CLICKUP_API_KEY = Config.CLICKUP_API_KEY
CLICKUP_LIST_ID = Config.CLICKUP_LIST_ID
SCORES_FIELD_ID = Config.SCORES_FIELD_ID
PLOT_FIELD_ID = Config.PLOT_FIELD_ID
ANSWERS_FIELD_ID = Config.ANSWERS_FIELD_ID
ROUTINES_FIELD_ID = Config.ROUTINES_FIELD_ID
TYPEFORM_API_KEY = Config.TYPEFORM_API_KEY
FORM_ID = Config.FORM_ID

LINK_SUMMARY_TITLE_FIELD_ID = Config.LINK_SUMMARY_TITLE_FIELD_ID
LINK_SUMMARY_SUMMARY_FIELD_ID = Config.LINK_SUMMARY_SUMMARY_FIELD_ID
LINK_SUMMARY_OPENAI_API_KEY = Config.LINK_SUMMARY_OPENAI_API_KEY

app = Flask(__name__)

client = OpenAI(api_key=LINK_SUMMARY_OPENAI_API_KEY)


def main():
    field_mapping = get_field_mapping()
    responses = get_responses()

@app.route('/')
def hello():
    return "Hello, Flask is working!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    field_mapping = get_field_mapping()
    responses = get_responses()

    if responses and field_mapping:
        answers = process_latest_response(responses, field_mapping)
        lastname = get_last_name(responses)
        if answers:
            integrated_data = integrate_answers(answers)

            assessment = HealthAssessment(
                integrated_data['exercise'],
                integrated_data['nutrition'],
                integrated_data['sleep'],
                integrated_data['social_connections'],
                integrated_data['stress_management'],
                integrated_data['gratitude'],
                integrated_data['cognition'],
            )
            exercise_score = float(assessment.exercise_assessment.report())
            nutrition_score = float(assessment.nutrition_assessment.report())
            sleep_score = float(assessment.sleep_assessment.report())
            social_connections_score = float(assessment.social_connections_assessment.report())
            stress_management_score = float(assessment.stress_management_assessment.report())
            gratitude_score = float(assessment.gratitude_assessment.report())
            cognition_score = float(assessment.cognition_assessment.report())
            total_score = float(assessment.calculate_total_score())

            scores = {
                "Movement&Exercise": exercise_score,
                "HealthfulNutrition": nutrition_score,
                "RestorativeSleep": sleep_score,
                "SocialEngagement": social_connections_score,
                "StressManagement": stress_management_score,
                "Gratitude&Reflection": gratitude_score,
                "Cognition": cognition_score
            }

            scores_values = [
                exercise_score, nutrition_score, sleep_score,
                social_connections_score, stress_management_score,
                gratitude_score, cognition_score
            ]

            categories = [
                'Exercise', 'Nutrition', 'Sleep', 'Social Connections',
                'Stress Management', 'Gratitude', 'Cognition'
            ]

            num_vars = len(categories)
            angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
            scores_values += scores_values[:1]
            angles += angles[:1]

            fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
            ax.fill(angles, scores_values, color='blue', alpha=0.25)
            ax.plot(angles, scores_values, color='blue', linewidth=2)

            ax.set_yticks(np.arange(0, 101, 10))
            ax.set_yticklabels(['0', '10', '20', '30', '40', '50', '60', '70', '80', '90', '100'])
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories)

            plt.title(f'Health Scores for {lastname}')
            #image_path = f"{lastname}_health_scores.png"
            image_path = os.path.join('/app', f"{lastname}_health_scores.png")
            plt.savefig(image_path)
            plt.show()
            plt.close()

            routines = load_routines()
            rules = load_rules()

            schedule = generate_schedule(answers, scores, routines, rules)
            routines = display_monthly_plan(schedule)
            task_id = create_clickup_task(lastname, scores, answers, total_score, routines,
                                           "")
            upload_file_to_clickup(task_id, image_path)
            os.remove(image_path)

    return jsonify({'status': 'success'}), 200

@app.route('/webhook-summary', methods=['POST'])
def webhook_summary():
    try:
        # Get data from ClickUp webhook
        data = request.json
        if not data or 'payload' not in data:
            return jsonify({"status": "error", "message": "Invalid data received"}), 400

        task_id = data['payload'].get('id')
        task_name = data['payload'].get('name')

        if not task_id or not task_name:
            return jsonify({"status": "error", "message": "Task ID or Task Name (URL) is missing"}), 400

        print(f"Processing task: {task_name}")

        # Fetch the content and title from the URL (task_name is the URL)
        page_title, page_content = fetch_url_content(task_name)

        # Check if there was an error while fetching the content
        if page_content.startswith("Error") or page_content.startswith("Authorization Failed"):
            summary = f"Site could not be scraped due to an exception: {page_content}"
        else:
            # Generate summary using GPT based on the page content
            summary = generate_summary(page_content)

        # Update ClickUp task with title (from the HTML <title> tag) and summary
        update_clickup_custom_field(task_id, LINK_SUMMARY_TITLE_FIELD_ID, page_title)
        update_clickup_custom_field(task_id, LINK_SUMMARY_SUMMARY_FIELD_ID, summary)

        return jsonify({
            "status": "success",
            "task_id": task_id,
            "title": page_title,
            "summary": summary
        })

    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


def fetch_url_content(url):
    """Fetches the HTML <title> and the content from the given URL and extracts meaningful text."""
    try:
        # Simulate a browser request by setting a User-Agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 403:
            # Handle 403 error specifically, return a message and skip
            print(f"Authorization failed for URL: {url}. Status code: {response.status_code}")
            return "Authorization Failed", "Content cannot be fetched due to authorization restrictions."

        if response.status_code != 200:
            raise Exception(f"Failed to fetch content from URL: {url}. Status code: {response.status_code}")

        # Parse the page with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the title from the HTML <title> tag
        page_title = soup.title.string if soup.title else "Untitled"

        # Find and return the content (adjust selectors based on the page structure)
        paragraphs = soup.find_all('p')  # Extract all paragraphs
        content = ' '.join([para.get_text() for para in paragraphs])

        if not content:
            raise Exception("No meaningful content found on the page.")

        return page_title, content

    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return "Network Error", "Content cannot be fetched due to a network issue."

    except Exception as e:
        # Log and return a safe response to continue the process
        print(f"Error fetching content from {url}: {e}")
        return "Error", f"Content could not be fetched. Error: {e}"


def generate_summary(text):
    """Generates a summary using OpenAI GPT based on the given text."""
    prompt = f"""
    Fasse den folgenden Text zusammen, achte dabei darauf zuerst eine Einordnung des Textes zu geben, danach gehe auf den Inhalt ein (verzichte auf Überschriften wie **Einordnung**):

    {text}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=4000
    )

    summary = response.choices[0].message.content.strip()
    return summary


def update_clickup_custom_field(task_id, field_id, value):
    url = f"https://api.clickup.com/api/v2/task/{task_id}/field/{field_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": CLICKUP_API_KEY
    }
    payload = {"value": value}

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print(f"Successfully updated ClickUp task {task_id} with {field_id}")
    else:
        print(f"Failed to update ClickUp task {task_id}. Response: {response.content}")
        raise Exception(f"Failed to update task {task_id}")




if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)