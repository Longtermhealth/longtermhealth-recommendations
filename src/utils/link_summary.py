# rule_based_system/utils/link_summary.py
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from src.config import Config

client = OpenAI(api_key=Config.LINK_SUMMARY_OPENAI_API_KEY)

def fetch_url_content(url):
    """Fetches the HTML <title> and the content from the given URL and extracts meaningful text."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 403:
            print(f"Authorization failed for URL: {url}. Status code: {response.status_code}")
            return "Authorization Failed", "Content cannot be fetched due to authorization restrictions."

        if response.status_code != 200:
            raise Exception(f"Failed to fetch content from URL: {url}. Status code: {response.status_code}")

        soup = BeautifulSoup(response.text, 'html.parser')

        page_title = soup.title.string if soup.title else "Untitled"

        paragraphs = soup.find_all('p')
        content = ' '.join([para.get_text() for para in paragraphs])

        if not content:
            raise Exception("No meaningful content found on the page.")

        return page_title, content

    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return "Network Error", "Content cannot be fetched due to a network issue."

    except Exception as e:
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

