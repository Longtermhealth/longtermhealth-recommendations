#pubmed_scraper.py

import requests
import json
from config import Config
from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
    ElementClickInterceptedException,
)

from bs4 import BeautifulSoup
from openai import OpenAI

app = Flask(__name__)
CORS(app)
CLICKUP_API_KEY = Config.CLICKUP_API_KEY
LINK_SUMMARY_OPENAI_API_KEY = Config.LINK_SUMMARY_OPENAI_API_KEY

client = OpenAI(api_key=LINK_SUMMARY_OPENAI_API_KEY)


TITLE_FIELD_ID = "130b6ed2-f463-458c-9fc4-87c7f3ae3ec0"
SUMMARY_FIELD_ID = "509194d4-25e8-4e13-b965-5d88a3ada3d3"
AUTHOR_FIELD_ID = "a7515969-06ff-4896-8d90-2737f0d2633d"
LINK_FIELD_ID = "1ace9523-41b2-4317-b47d-e1b3a5e14835"
SLIDES_FIELD_ID = "4c4a2fde-4ec5-42d1-b6ab-79d4bf12cea7"
SLIDES_TOV_FIELD_ID = "279d2b7d-4a16-410a-89b3-34349ff9ba82"
METATAGS_FIELD_ID = "be769efc-21c2-451a-878b-bbaf528eb1b2"
ROUTINES_FIELD_ID = "8ebd4839-f9f9-48ba-9c38-e60aabb42726"
KEYWORDS_FIELD_ID = "e2aed406-58c4-4482-9952-68d6b0f5296b"
ROUTINE_1_FIELD_ID = "a0b63ba5-c486-4913-9db9-7d8efde31c89"
ROUTINE_2_FIELD_ID = "d1c1b0f2-e1f8-4d8f-9f64-be526b259a34"
ROUTINE_3_FIELD_ID = "93ecc853-5952-4e9a-9fad-8dd7236bb87d"



@app.route('/')
def home():
    print("Home route accessed.")
    return "webhook-pubmed server is running!"


@app.route('/webhook-pubmed', methods=['POST'])
def webhook():
    """
    Main endpoint that receives POST data from ClickUp.
    - Expects JSON with 'payload' containing 'id' (task_id) and 'name' (task_name).
    - The task_name is used as the URL.
    - We run call_external_script(url), then parse the results, generate summary, etc.
    - Then we update the relevant ClickUp fields in the given task.
    """
    print("Webhook triggered.")
    try:
        data = request.json
        print(f"Received data: {data}")
        if not data or 'payload' not in data:
            print("Invalid data received.")
            return jsonify({"status": "error", "message": "Invalid data received"}), 400

        task_id = data['payload'].get('id')
        task_name = data['payload'].get('name')
        description = data['payload'].get('description', '')

        if not task_id or not task_name:
            print("Task ID or Task Name is missing.")
            return jsonify({"status": "error", "message": "Task ID or Task Name is missing"}), 400

        print(f"Task ID: {task_id}, Task Name: {task_name}")


        url = task_name
        print(f"Starting to call external script with URL: {url}")
        extracted_info = call_external_script(url)
        print(f"Extracted info: {extracted_info}")


        if isinstance(extracted_info, str):
            print("Extracted info is an error message.")
            if ("Timeout occurred" in extracted_info or
                    "WebDriver error" in extracted_info or
                    "An error occurred" in extracted_info or
                    "No full text available" in extracted_info or
                    "Failed to extract information" in extracted_info):
                print("Handling error by updating ClickUp fields.")
                update_clickup_custom_field(task_id, TITLE_FIELD_ID, "no pmc link found")
                update_clickup_custom_field(task_id, LINK_FIELD_ID, url)
                return jsonify({"status": "error", "message": extracted_info}), 500


        summary = create_summary(extracted_info['full_text'])
        print(f"Summary created: {summary}")
        first_author = extracted_info['first_author']
        title = extracted_info['title']

        print("Updating ClickUp custom fields with extracted information.")
        update_clickup_custom_field(task_id, SUMMARY_FIELD_ID, summary)
        update_clickup_custom_field(task_id, AUTHOR_FIELD_ID, first_author)
        update_clickup_custom_field(task_id, LINK_FIELD_ID, url)
        update_clickup_custom_field(task_id, TITLE_FIELD_ID, title)

        print(f"################################################################## ClickUp task updated")


        slides_tov = create_slides_tov(summary)
        print(f"Slides TOV created: {slides_tov}")
        update_clickup_custom_field(task_id, SLIDES_TOV_FIELD_ID, slides_tov)


        update_clickup_task_name(CLICKUP_API_KEY, task_id, title)


        metatags = create_metatags(slides_tov)
        print(f"Metatags created: {metatags}")
        update_clickup_custom_field(task_id, METATAGS_FIELD_ID, metatags)


        unformatted_output = create_routines(slides_tov)
        print(f"Routines created: {unformatted_output}")
        extracted_json = extract_json(unformatted_output)
        print(f"Extracted JSON: {extracted_json}")
        update_clickup_custom_field(task_id, ROUTINES_FIELD_ID, unformatted_output)

        response = {
            "status": "success",
            "task_id": task_id,
            "task_name": task_name,
            "description": description,
            "url": url,
            "summary": summary,
            "metatags": metatags,
            "routines": unformatted_output
        }
        print(f"Response prepared: {response}")
        return jsonify(response)

    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()
        if 'task_id' in locals():
            print("Updating ClickUp task name to indicate failure.")
            update_clickup_task_name(CLICKUP_API_KEY, task_id, "no pmc link found")
        return jsonify({"status": "error", "message": str(e)}), 500


def update_clickup_task_name(CLICKUP_API_KEY, task_id, title):
    print(f"Updating ClickUp task name for Task ID: {task_id} to '{title}'.")
    url = f'https://api.clickup.com/api/v2/task/{task_id}'
    payload = {'name': title}
    headers = {
        'Authorization': CLICKUP_API_KEY,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.put(url, json=payload, headers=headers)
        print(f"ClickUp API response status: {response.status_code}")
        if response.status_code == 200:
            print('Task name updated successfully!')
            return 'Task name updated successfully!'
        else:
            print(f'Failed to update task name. Status code: {response.status_code}, Response: {response.text}')
            return f'Failed to update task name. Status code: {response.status_code}, Response: {response.text}'
    except Exception as e:
        print(f"Exception occurred while updating task name: {e}")
        return f"Exception occurred: {e}"


def update_clickup_custom_field(task_id, field_id, value):
    print(f"Updating ClickUp custom field '{field_id}' for Task ID: {task_id} with value: {value}")
    url = f"https://api.clickup.com/api/v2/task/{task_id}/field/{field_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": CLICKUP_API_KEY
    }
    payload = {
        "value": value
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"ClickUp custom field update response status: {response.status_code}")
        if response.status_code != 200:
            print(f"Failed to update ClickUp task: {response.content}")
            raise Exception("Failed to update ClickUp task")
        print("Successfully updated ClickUp task field.")
    except Exception as e:
        print(f"Exception occurred while updating ClickUp custom field: {e}")
        traceback.print_exc()
        raise



def create_summary(text):
    """
    Creates a summary in German with a minimum length of ~1000 words,
    using OpenAI. Adjust tokens/temperature as needed.
    """
    print("Creating summary using OpenAI API.")
    prompt = f"""
        Deine Aufgaben umfassen das Zusammenfassen von Informationen, sowie das Übersetzen von englischen Texten ins Deutsche. Schreibe mindestens 1000 Wörter pro Thema, damit es möglichst ausführlich wiedergegeben wird.

        Hier ist der Text: {text}
        """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Deine Aufgaben umfassen das Zusammenfassen von Informationen, sowie das Übersetzen von englischen Texten ins Deutsche."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=4000
        )
        summary = response.choices[0].message.content.strip()
        print("Summary created successfully.")
        return summary
    except Exception as e:
        print(f"Error creating summary: {e}")
        traceback.print_exc()
        return ""


def create_slides(content, title, first_author):
    """
    Creates slides with a specific style and structure.
    (Currently not used in final logic, but included for reference.)
    """
    print("Creating slides using OpenAI API.")
    prompt = f"""
         Du bist der virtuelle Assistent einer Mobile Health App, die wissenschaftlich fundierte Informationen vermittelt und Nutzer mit Hilfe von Gewohnheiten und Routinen zu einem gesünderen Leben motiviert. Dein Tonfall sollte immer sachlich, präzise und professionell sein, um Vertrauen zu gewinnen und zu erhalten. Gleichzeitig solltest du positiv, unterstützend und inspirierend sein, um die Nutzer zu motivieren. Deine Kommunikation sollte persönlich und empathisch sein, um eine enge Beziehung zu den Nutzern aufzubauen. Verwende eine klare und einfache Sprache, damit die Informationen leicht verständlich sind. Außerdem solltest du die Nutzer aktiv einbeziehen und zur Interaktion ermutigen.

         Beispiele:

             Wissenschaftlich fundiert und vertrauenswürdig:
             „Neueste Studien zeigen, dass regelmäßige Bewegung das Risiko für Herz-Kreislauf-Erkrankungen erheblich senken kann. Unsere Tipps basieren auf diesen wissenschaftlichen Erkenntnissen, um dir zu helfen, gesünder zu leben.“

             Unterstützend und motivierend:
             „Du hast heute bereits 5.000 Schritte gemacht – das ist großartig! Setze dir kleine, erreichbare Ziele und feiere jeden Fortschritt. Wir sind hier, um dich auf deinem Weg zu einem gesünderen Leben zu unterstützen.“

             Persönlich und empathisch:
             „Wir wissen, dass es manchmal schwer sein kann, gesunde Gewohnheiten beizubehalten. Denke daran, dass jeder Schritt zählt und dass du nicht allein bist. Lass uns gemeinsam kleine Schritte zu einem gesünderen Leben machen.“

             Klar und einfach verständlich:
             „Trinke täglich mindestens 1,5 Liter Wasser, um deinen Körper hydratisiert und gesund zu halten. Wasser ist essenziell für viele Körperfunktionen und hilft dir, dich energiegeladen zu fühlen.“

             Engagierend und interaktiv:
             „Hast du unsere neuen Übungen schon ausprobiert? Teile deine Fortschritte mit uns und der Community – gemeinsam sind wir stärker!“

         Antworte auf alle Anfragen der Nutzer in diesem Stil und achte darauf, dass deine Antworten alle genannten Elemente enthalten.

         Aufgabe: Du bist ein Content Generator für eine Mobile Health App. Deine Rolle ist es, Texte oder Links, die dir gegeben werden, effektiv zu verarbeiten. Deine Aufgaben ist die Umwandlung dieser Informationen in leicht verdauliche Wissenshappen für die Nutzer der App. Die Inhalte sollten schrittweise komplexer werden und in einem interaktiven Slide-Format präsentiert werden. Denk daran, dass die Zielgruppe medizinische Begriffe nicht kennt. Daher solltest du Fremdwörter erklären, wenn sie zum ersten Mal im Text vorkommen. Erkläre Begriffe wie z.B. "aerobe Kapazität".

         Anleitung:

         Slide "Intro"
         Erstelle eine Überschrift und eine Subheadline im Stil einer Zeitung, die den Kern des Themas einfängt.

         Slide "Details"
         Biete erste grundlegende Informationen oder Fakten zum Thema.
         Die Informationen sollten auf dieser Slide noch allgemein und einleitend sein, um Interesse zu wecken.
         Schreibe mindestens 5 Zeilen.

         Slide "Vertiefung"
         Erkläre das Thema genauer und gehe auf spezielle Aspekte ein, die auf den vorherigen Slides nur angeschnitten wurden.
         ACHTUNG: HIER MINDESTENS FÜNFZEHN ZEILEN!!! Teile die Vertiefung auf mehrere Slides auf und verwende zusätzlich Bulletpoints!

         Slide "Schon gewusst?"
         Präsentiere interessante, weniger bekannte Fakten oder Statistiken, die das Verständnis vertiefen. Achte darauf den Fakt mit einer Textstelle zu belegen!
         Schreibe 1 Zeile und überprüfe, dass der Fakt nur aus dem gegebenen Text kommt!

         Studien Slide (Wissenschaftliche Grundlage)
         Dann schreib einen Absatz mit 5 Zeilen für die Zusammenfassung der Studienergebnisse.
         Wichtig: Nenne den Namen der Studie {title} und den Namen des ersten Autors {first_author} im Fließtext. Achte dabei darauf das Format anzupassen. Achtung, nur ein Beispiel: "Max Mustermann" wird zu "Mustermann et Al.".
         Stelle danach die Schlussfolgerungen oder Ergebnisse der Studie dar.
         Schreibe mindestens 5 Zeilen.

         Zusätzliche Hinweise:
         Achte darauf, dass die Information fließend und logisch von einer Slide zur nächsten übergeht, wobei jede Slide auf dem Wissen der vorherigen aufbaut.
         Verwende immer die Du-Form.
         Frage nicht nach, ob du fortfahren sollst. Erstelle alle Slides auf einmal.
         Schreibe keine Einleitung und keinen Schluss Satz.

         Hier ist der Text: {content}
         """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        slides = response.choices[0].message.content.strip()
        print("Slides created successfully.")
        return slides
    except Exception as e:
        print(f"Error creating slides: {e}")
        traceback.print_exc()
        return ""


def create_slides_tov(content):
    """
    Creates a TOV (tone-of-voice) version of the slides.
    This is what's actually used in the final logic.
    """
    print("Creating slides TOV using OpenAI API.")
    prompt = f"""
    Du bist der virtuelle Assistent einer Mobile Health App, die wissenschaftlich fundierte Informationen vermittelt und Nutzer mit Hilfe von Gewohnheiten und Routinen zu einem gesünderen Leben motiviert. Dein Tonfall sollte immer sachlich, präzise und professionell sein, um Vertrauen zu gewinnen und zu erhalten. Unser Ansatz ist streng wissensbasiert, die Sprache sollte somit nicht nach Spekulation oder zu wage klingen. Gleichzeitig solltest du positiv, freundlich, zugänglich und unterstützend sein. Es ist wichtig, die Nutzer zu inspirieren und letztendlich zu motivieren. Die Sprache sollte somit eine „yes we can“ Attitüde vermitteln und nicht steif wirken. Deine Kommunikation sollte persönlich (wir sprechen User mit „Du“ an), ehrlich, authentisch und empathisch sein, um eine enge Beziehung zu den Nutzern aufzubauen. Die Nutzer sollen aktiv einbezogen und zur Interaktion ermutigt werden.  Wir stehen für eine tolerante, weltoffene und multikulturelle Gesellschaft. In diesem Zusammenhang sollte die Sprache gender-neutral sein, im Deutschen verwenden wir die Schreibweise mit Doppelpunkt, also z.B. Ärzt:innen bzw. vermeiden das Gendern, in dem wir die Begriffe umschreiben (z.B. „die Wissenschaft zeigt…“ anstatt „Wisschenschaftler:innen zeigen“).

    Verwende eine klare und einfache Sprache, damit die Vermittlung von Informationen leicht verständlich und so inklusiv wie möglich ist. Fachbegriffe sollten deshalb weitestgehend vermieden oder erklärt werden, Texte sollten nicht zu medizinisch oder „von der Fachperson zum Laien“ (von oben herab, predigend) sein. 

    Emojis:
    nur relevante und positive Emojis verwenden und wenn diese den Text unterstützen. Generell sparsam mit Emojis umgehen.

    Beispiele: 
    Wissenschaftlich fundiert und vertrauenswürdig: 
    „Neueste Studien zeigen, dass vor allem regelmäßige Bewegung das Risiko für eine Herz-Kreislauf-Erkrankung erheblich senken kann. Unsere Tipps basieren ausschließlich auf wissenschaftlichen Erkenntnissen, um dir beim Erreichen deiner Gesundheitsziele zu helfen.“

    Unterstützend und motivierend: 
    „Du hast heute bereits 5.000 Schritte gemacht – wunderbar! Wir sind hier, um dich auf deinem Weg zu einem gesünderen Leben zu unterstützen. Schritt für Schritt.“ 

    Persönlich und empathisch: 
    „Nobody is perfect. Wir wissen, wie schwer es sein kann, neue Gewohnheiten anzunehmen. Denke einfach daran, dass jeder noch so kleine Schritt zählt. Lass es uns gemeinsam noch einmal versuchen!“ 

    Klar und einfach verständlich: 
    „Versuche täglich mindestens 1,5 Liter Flüssigkeiten zu dir zu nehmen. Eine gute Wasserversorgung hat viele Vorteile, wie z.B. den Erhalt wichtiger Körperfunktionen, eine glattere Haut sowie mehr Energie.“ 

    Engagierend, frisch und interaktiv: 
    „Hast du unsere neuen Übungen schon ausprobiert? Teile deine Fortschritte mit uns und der Community – gemeinsam sind wir stärker!“ 

    Antworte auf alle Anfragen der Nutzer in diesem Stil und achte darauf, dass deine Antworten alle genannten Elemente enthalten.


    Negativbeispiel für zu medizinisch und von der Fachperson zum Laien:
    „In Folge eines Mangels an Mangel an Intrinsic-Faktor (IF) kommt es zur Ausprägung einer chronisch-atrophischen Gastritis vom Typ A (Autoimmungastritis) mit nachfolgender Entwicklung einer perniziösen Anämie.“

    Negativbeispiel für Zeigefinger:
    „Wenn du nicht täglich deine Übungen machst wird es unmöglich sein, deine gesetzten Ziele zu erreichen.“

    Antworte auf alle Anfragen der Nutzer in diesem Stil und achte darauf, dass deine Antworten alle genannten Elemente enthalten.

    Aufgabe: Du bist ein Content Generator für eine Mobile Health App. Deine Rolle ist es, Texte oder Links, die dir gegeben werden, effektiv zu verarbeiten. Deine Aufgaben ist die Umwandlung dieser Informationen in leicht verdauliche Wissenshappen für die Nutzer der App. Die Inhalte sollten schrittweise komplexer werden und in einem interaktiven Slide-Format präsentiert werden. Denk daran, dass die Zielgruppe medizinische Begriffe nicht kennt. Daher solltest du Fremdwörter erklären, wenn sie zum ersten Mal im Text vorkommen. Erkläre Begriffe wie z.B. "aerobe Kapazität".

    Anleitung:

    Slide "Intro"
    Erstelle eine Überschrift und eine Subheadline im Stil einer Zeitung, die den Kern des Themas einfängt.

    Slide "Details"
    Biete erste grundlegende Informationen oder Fakten zum Thema.
    Die Informationen sollten auf dieser Slide noch allgemein und einleitend sein, um Interesse zu wecken.
    Schreibe mindestens 5 Zeilen.

    Slide "Vertiefung"
    Erkläre das Thema genauer und gehe auf spezielle Aspekte ein, die auf den vorherigen Slides nur angeschnitten wurden.
    ACHTUNG: HIER MINDESTENS FÜNFZEHN ZEILEN!!! Teile die Vertiefung auf mehrere Slides auf und verwende zusätzlich Bulletpoints!

    Slide "Schon gewusst?"
    Präsentiere interessante, weniger bekannte Fakten oder Statistiken, die das Verständnis vertiefen. Achte darauf den Fakt mit einer Textstelle zu belegen!
    Schreibe 1 Zeile und überprüfe, dass der Fakt nur aus dem gegebenen Text kommt!

    Zusätzliche Hinweise:
    Achte darauf, dass die Information fließend und logisch von einer Slide zur nächsten übergeht, wobei jede Slide auf dem Wissen der vorherigen aufbaut.
    Verwende immer die Du-Form.
    Frage nicht nach, ob du fortfahren sollst. Erstelle alle Slides auf einmal.
    Schreibe keine Einleitung und keinen Schluss Satz.

    Hier ist der Text: {content}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        slides_tov = response.choices[0].message.content.strip()
        print("Slides TOV created successfully.")
        return slides_tov
    except Exception as e:
        print(f"Error creating slides TOV: {e}")
        traceback.print_exc()
        return ""


def create_metatags(slides):
    """
    Creates 'metatags' in JSON format using a structured schema.
    """
    print("Creating metatags using OpenAI API.")
    prompt = f"""
    Aufgabe: Erstelle eine strukturierte Datentabelle mit den folgenden Attributen basierend auf den Vorgaben:

    Input-Beschreibung:
    Generiere Daten für eine Aktivität oder Routine. Die Daten müssen die folgenden Attribute enthalten:

        ID: Eindeutige Identifikationsnummer der Aktivität.
        filterContentTags: Tags, die die Aktivität beschreiben (z. B. "cardio, weightloss").
        Name_en: Englischer Name der Aktivität.
        Notes: Zusätzliche Hinweise oder Notizen zur Aktivität.
        Package: Name des zugehörigen Pakets, falls zutreffend.
        Package Type: Typ des Pakets (z. B. Routine, Programm).
        PackageRoutineID: ID der zugehörigen Routine oder des Pakets.
        RoutineCategory: Kategorie der Routine (z. B. Bewegung, Ernährung).
        MinRecurringDate: Minimale Wiederholungsfrequenz der Aktivität.
        Name: Deutscher Name der Aktivität.
        cleanedNames: Aufbereitete Namen oder Alternativen.
        Description: Beschreibung der Aktivität mit Fokus auf Nutzen und Zielgruppe.
        Order: Reihenfolge in einer Serie oder Liste.
        Variations: Variationen der Aktivität.
        Tag: Tags für die Aktivität.
        muscleTags: Tags für die betroffenen Muskelgruppen.
        Amount: Dauer oder Anzahl.
        AmountUnit: Einheit der Dauer (z. B. Minuten, Wiederholungen).
        Duration: Gesamtdauer.
        Check: Zusätzliche Validierungshinweise.
        Sets: Anzahl der Sätze.
        Period: Wiederholungszeitraum.
        Minimum / Recommended: Minimale und empfohlene Durchführung.
        Season: Geeignete Jahreszeit.
        PrimaryPillar_enum: Primärer Schwerpunkt der Aktivität (z. B. Bewegung, Ernährung).
        Category: Kategorie der Aktivität.
        Impact_Category / Impact_Subcategory: Haupt- und Unterkategorien des Effekts.
        SecondaryPillar: Sekundärer Schwerpunkt.
        Benefits (1-17): Nutzen mit Beschreibung und Wirkung.
        Difficulty: Schwierigkeitsgrad der Aktivität.
        Expert_Tip: Expertenhinweis.
        Time_of_Day: Geeignete Tageszeit.
        Location_enum / Location_description: Ort und Beschreibung des Standorts.
        Instructions: Anleitungen zur Durchführung.
        Equipment_needed: Benötigte Ausrüstung.
        Fitness_Level_Required: Erforderliches Fitnessniveau.
        Adaptability: Anpassungsmöglichkeiten (leicht und schwierig).
        Contraindication: Gegenanzeigen.
        Group_Activity: Ob es sich um eine Gruppenaktivität handelt.
        Media Links: Bilder und Videos.
        SourceOfRecommendation: Quelle der Empfehlung.
        Which_Tracker_Needed: Benötigte Tracker.
        Routine_Timeframe: Zeitrahmen für die Routine.
        EducationArticleLink: Link zu einem Bildungsartikel.

    Beispiel-Ausgabe (Das Format ist JSON):
      "ID": 1,
      "filterContentTags": "description",
      "Name_en": "walking 20 minutes",
      "Notes": "",
      "Package": "",
      "Package Type": "",
      "PackageRoutineID": "",
      "RoutineCategory": "MOVEMENT",
      "MinRecurringDate": "WEEKLY",
      "Name": "Spazierengehen 20 Minuten",
      "cleanedNames": "Spazierengehen",
      "Description": "Spazierengehen ist eine sanfte Cardioaktivität, die hauptsächlich die Herz-Kreislauf-Gesundheit unterstützt und die Ausdauer verbessert.",
      "order": 1,
      "Variations": "walking",
      "Tag": "cardio, LTH basic, weightloss, Immunesystem, usertest",
      "muscleTags": "hips (primary), calves (secondary), quadriceps (secondary), hamstrings (secondary), glutes (tertiary), abs (tertiary), obliques (tertiary), deltoids (tertiary), biceps (tertiary), triceps (tertiary)",
      "Amount": 20,
      "AmountUnit": "minutes",
      "AmountUnit_description": "Min.",
      "AmountUnit_enum": "MINUTES",
      "Duration": 20,
      "DurationUnit": "m",
      "Check": "Übereinstimmung",
      "Sets": 0,
      "Period": "WEEKLY",
      "Minimum": 2,
      "Recommended": 7,
      "Season": "",
      "PrimaryPillar_enum": "MOVEMENT",
      "PrimaryPillar_description": "Bewegung",
      "Category": "LOW_IMPACT",
      "Impact_Category": "2",
      "Subcategory": "WALKING",
      "Impact_Subcategory": "2",
      "SecondaryPillar": "SLEEP",
      "Category_2": "SLEEP_AIDS_AND_NATURAL_SLEEP_REMEDIES",
      "Impact_Category_2": "2",
      "Subcategory_2": "SPORT",
      "Impact_Subcategory_2": "5",
      "impactMovement": 2,
      "impactNutrition": 0,
      "impactSleep": 1,
      "impactStress": 2,
      "impactSocial": 0,
      "impactGratitude": 0,
      "impactCognitive": 1,
      "Intensity_Time": 2,
      "Intensity_Physical": 2,
      "Intensity_Mental": 2,
      "Intensity_Emotional": 1,
      "Intensity_Social": 1,
      "Intensity_Frequency": 5,
      "Goal": "CARDIO_BUILDING",
      "1_Benefit": "ENDURANCE",
      "1_Benefit_name": "Verbesserte körperliche Fitness",
      "1_Benefit_description": "Spazierengehen ist eine sanfte und effektive Möglichkeit, die körperliche Fitness zu fördern und die Ausdauer zu steigern.",
      "1_Benefit_Impact": 2,
      "2_Benefit": "WEIGHT_LOSS",
      "2_Benefit_Impact": 1,
      "2_Benefit_name": "Gewichtsreduktion",
      "2_Benefit_description": "Durch Kalorienverbrennung beim Gehen kann Übergewicht reduziert werden, da der Energieverbrauch steigt.",
      "3_Benefit": "IMPROVE_IMMUNITY",
      "3_Benefit_Impact": 1,
      "3_Benefit_name": "Stärkung des Immunsystems",
      "3_Benefit_description": "Regelmäßige Bewegung fördert die Immunabwehr, indem sie die Zirkulation von Immunzellen verbessert.",
      "4_Benefit": "ANTIINFLAMMATION",
      "4_Benefit_Impact": 2,
      "4_Benefit_name": "Entzündungshemmende Wirkung",
      "4_Benefit_description": "Bewegung reduziert Entzündungen, da sie die Ausschüttung entzündungshemmender Stoffe anregt.",
      "5_Benefit": "INSULINE_RESISTANCE",
      "5_Benefit_Impact": 2,
      "5_Benefit_name": "Verbesserung der Insulinempfindlichkeit",
      "5_Benefit_description": "Durch regelmäßiges Spazierengehen wird die Insulinempfindlichkeit gesteigert, was den Blutzucker reguliert.",
      "6_Benefit": "BOOSTS_MOOD",
      "6_Benefit_Impact": 1,
      "6_Benefit_name": "Stimmungsverbesserung",
      "6_Benefit_description": "Körperliche Aktivität fördert die Ausschüttung von Endorphinen, die die Stimmung heben.",
      "7_Benefit": "BONE_DENSITY",
      "7_Benefit_Impact": 1,
      "7_Benefit_name": "Verbesserte Knochendichte",
      "7_Benefit_description": "Regelmäßige Belastung der Knochen fördert deren Dichte, da der Knochenabbau gehemmt wird.",
      "8_Benefit": "BETTER_BODY_RESISTANCE",
      "8_Benefit_Impact": 2,
      "8_Benefit_name": "Erhöhte körperliche Widerstandskraft",
      "8_Benefit_description": "Durch Bewegung wird die Fitness gesteigert, was die Fähigkeit erhöht, körperlichen Anforderungen standzuhalten.",
      "9_Benefit": "IMPROVES_LUNG_FUNCTION",
      "9_Benefit_Impact": 2,
      "9_Benefit_name": "Verbesserte Lungenfunktion",
      "9_Benefit_description": "Körperliche Aktivität fördert die Atemkapazität und stärkt die Lungenmuskulatur.",
      "10_Benefit": "HEART_HEALTH",
      "10_Benefit_Impact": 1,
      "10_Benefit_name": "Verbesserte Herzgesundheit",
      "10_Benefit_description": "Durch regelmäßige Bewegung wird das Herz-Kreislauf-System gestärkt, was das Risiko von Erkrankungen senkt.",
      "11_Benefit": "STRESS_REDUCTION",
      "11_Benefit_Impact": 2,
      "11_Benefit_name": "Stressreduktion",
      "11_Benefit_description": "Aktivität wie Spazierengehen hat einen positiven Einfluss auf Stress, da sie Stresshormone abbaut.",
      "12_Benefit": "PROMOTE_CIRCULATION",
      "12_Benefit_Impact": 2,
      "12_Benefit_name": "Förderung der Durchblutung",
      "12_Benefit_description": "Bewegung regt die Blutzirkulation an, wodurch der Sauerstofftransport im Körper verbessert wird.",
      "13_Benefit": "NATURE",
      "13_Benefit_Impact": 3,
      "13_Benefit_name": "Verbundenheit mit der Natur",
      "13_Benefit_description": "Das Spazieren in der Natur fördert das Wohlbefinden und reduziert Stress durch beruhigende Umgebungen.",
      "14_Benefit": "LOWERS_CHOLESTEROL_RISK",
      "14_Benefit_Impact": 1,
      "14_Benefit_name": "Gesenkter Cholesterinspiegel",
      "14_Benefit_description": "Regelmäßige Bewegung hilft, den Cholesterinspiegel zu regulieren, indem sie das HDL-Cholesterin erhöht.",
      "15_Benefit": "IMPROVES_MENTAL_HEALTH",
      "15_Benefit_Impact": 3,
      "15_Benefit_name": "Verbesserte mentale Gesundheit",
      "15_Benefit_description": "Körperliche Aktivitäten fördern das emotionale Gleichgewicht und reduzieren Angstzustände durch Endorphinausschüttung.",
      "16_Benefit": "PREVENTS_CANCER",
      "16_Benefit_Impact": 3,
      "16_Benefit_name": "Krebsprävention",
      "16_Benefit_description": "Regelmäßige Bewegung kann das Risiko von bestimmten Krebsarten verringern, indem sie den Stoffwechsel reguliert.",
      "Difficulty": "VERY_EASY",
      "Expert_Tip": "",
      "Time_of_Day": "ANY",
      "Location_enum": "OUTDOOR",
      "Location_description": "Draußen",
      "Instructions": "Keine detaillierte Anleitung erforderlich.",
      "Instructions_english": "",
      "Equipment_needed_enum": "NONE",
      "Equipment_needed_description": "Kein Equipment benötigt", 
      "Fitness_Level_Required": "UNFIT",
      "AdaptabilityEasy": "Wenn du das Spazierengehen erleichtern möchtest, kannst du dich an eine Wand oder ein Geländer lehnen, um mehr Stabilität zu bekommen. Alternativ kannst du einen Widerstandsband verwenden, um den Bewegungsbereich zu unterstützen.",
      "adaptabilityHard": "Erhöhe die Geschwindigkeit für Teilstrecken, um die Intensität zu steigern.",
      "Contraindication": "legs, feet, back, knees, hips, joints",
      "Group_Activity": "CAN_BE",  
      "SourceOfRecommendation": "Questionnaire",
      "Which_Tracker_Needed": "EXERCISE",
      "Wearable_Data": "Watch, Ring"



    Anweisung:

        Erstelle eine ähnliche Datentabelle für jede Aktivität mit den oben genannten Attributen.
        Nutze klare und präzise Beschreibungen.
        Achte auf die korrekte Zuordnung der Attribute.
        Schreibe keine Einleitung und auch keine Zusammenfassung, stell einfach nur das json bereit.


    Hier ist der Inhalt: {slides}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        metatags = response.choices[0].message.content.strip()
        print("Metatags created successfully.")
        return metatags
    except Exception as e:
        print(f"Error creating metatags: {e}")
        traceback.print_exc()
        return ""


def create_routines(slides):
    """
    Creates routines in JSON format.
    """
    print("Creating routines using OpenAI API.")
    prompt = f"""
    Erstelle 1 Routine in folgendem Format für den gegebenen Text. Achte dabei darauf eine leichte Schwierigkeitsstufen wiederzugeben. 
    Das Format ist JSON. 



    Aufbau:
    ### 1. **Routinen-Identifikation**

    - **Routine_ID**: Eindeutige Identifikationsnummer für jede Routine.
    - **Routine_Name**: Klarer und beschreibender Name der Routine.

    ### 2. **Kategorisierung**

    - **Category**: Kategorie der Routine (z.B. Bewegung und Training, Gesunde Ernährung, etc.).
    - **Subcategory**: Unterkategorie, falls zutreffend (z.B. Yoga, Cardio unter Bewegung und Training).

    ### 3. **Zeit und Häufigkeit**

    - **Frequency**: Wie oft die Routine durchgeführt werden sollte (z.B. täglich, wöchentlich).
    - **Duration**: Durchschnittliche Dauer der Routine in Minuten.
    - **Time_of_Day**: Empfohlene Tageszeit für die Routine (z.B. Morgen, Abend).

    ### 4. **Ziel und Nutzen**

    - **Goal**: Primäres Ziel der Routine (z.B. Muskelaufbau, Entspannung, soziale Interaktion).
    - **Benefits**: Liste der gesundheitlichen Vorteile (z.B. verbesserter Schlaf, reduzierter Stress).

    ### 5. **Schwierigkeitsgrad**

    - **Difficulty**: Schwierigkeitsgrad der Routine (z.B. Anfänger, Fortgeschritten, Experte).

    ### 6. **Benötigte Ressourcen**

    - **Equipment_Needed**: Ob und welche Ausrüstung benötigt wird (z.B. Yoga-Matte, keine Ausrüstung).
    - **Location**: Empfohlener Ort für die Durchführung (z.B. Zuhause, Fitnessstudio).

    ### 7. **Anleitung und Inhalte**

    - **Instructions**: Schritt-für-Schritt-Anleitung zur Durchführung der Routine.
    - **Multimedia_Content**: Links zu Videos, Bildern oder Audioanweisungen, falls vorhanden.

    ### 8. **Personalisierung und Anpassung**

    - **User_Adaptability**: Wie gut die Routine an individuelle Bedürfnisse angepasst werden kann.
    - **Feedback_Mechanism**: Möglichkeit zur Rückmeldung durch den Nutzer (z.B. Bewertung der Effektivität).

    ### 9. **Verlaufsdaten und Tracking**

    - **Completion_Status**: Status, ob die Routine abgeschlossen wurde (True/False).
    - **User_Feedback**: Bewertung und Kommentare des Nutzers zur Routine.
    - **Date_Last_Completed**: Datum, an dem die Routine zuletzt durchgeführt wurde.
    - **Frequency_Completed**: Wie oft die Routine innerhalb eines bestimmten Zeitraums abgeschlossen wurde.

    Der Output sollte wie folgt strukturiert sein. Achte darauf, dass der Output genau so wie folgt strukturiert ist:

    {{
        "data": [
            {{
                "Routine_ID": 1,
                "Routine_Name": "Leichtes Joggen",
                "Category": "Bewegung und Training",
                "Subcategory": "Cardio-Training",
                "Frequency": "1x/Woche",
                "Duration": 10,
                "Time_of_Day": "Morgens",
                "Goal": "Fitness verbessern, Gewichtsabnahme",
                "Benefits": ["Sonnenlicht", "Besserer Schlaf", "Kreislauf in Schwung bringen"],
                "Difficulty": "Anfänger",
                "Equipment_Needed": "Keine",
                "Location": "Draußen",
                "Instructions": "Beginnen Sie mit einem leichten Joggen für 10 Minuten. Achten Sie darauf, in einem gleichmäßigen Tempo zu laufen, das für Sie angenehm ist.",
                "Multimedia_Content": [],
                "User_Adaptability": "Kann je nach Fitnesslevel angepasst werden",
                "Feedback_Mechanism": "Nutzer kann die Effektivität bewerten",
                "Completion_Status": false,
                "User_Feedback": "",
                "Date_Last_Completed": "",
                "Frequency_Completed": 0
            }}



    Hier ist der Text: {slides}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        routines = response.choices[0].message.content.strip()
        print("Routines created successfully.")
        return routines
    except Exception as e:
        print(f"Error creating routines: {e}")
        traceback.print_exc()
        return ""


def extract_json(content):
    """
    Just a helper that attempts to strip backticks or `json` fences
    from the final JSON-like content.
    """
    print("Extracting JSON from content.")
    trimmed_content = content.strip().strip('```json').strip().strip('```')
    print(f"Trimmed content: {trimmed_content}")
    return trimmed_content



def call_external_script(url):
    """
    Unified function that:
      1) Opens Selenium
      2) Loads the PubMed page
      3) Checks which publisher link is available using check_buttons
      4) Clicks the link if found
      5) Switches to the new window
      6) Runs the specialized scraper for that publisher
      7) Returns a dictionary with {title, first_author, full_text}
         or returns a string if an error occurs
    """
    driver = None
    try:
        driver = initialize_webdriver()
        driver.get(url)

        results = check_buttons(driver, url)
        # Filter out only True results
        available_choices = {k: v for k, v in results.items() if v == True}

        if not available_choices:
            return "No full text available from recognized publishers."

        scraper_map = {
            "PubMed Central Free Full Text": (
                ".//a[contains(@class, 'pmc')]",
                pubmed_scrape,
                By.CLASS_NAME,
                "main-article-body"
            ),
            "Elsevier Open Access": (
                ".//a[contains(@href, 'linkinghub.elsevier.com/retrieve/pii/')]",
                call_elsevier_script,
                By.CSS_SELECTOR,
                "span.title-text"
            ),
            "CellPress Open Access": (
                ".//a[contains(@href, 'linkinghub.elsevier.com/retrieve/pii/S2211-1247')]",
                call_elsevier_script,
                By.CSS_SELECTOR,
                "span.title-text"
            ),
            "MDPI Full Text Open Access": (
                ".//a[contains(@href, 'mdpi.com/resolver')]",
                call_mdpi_script,
                By.CSS_SELECTOR,
                "h1.title.hypothesis_container"
            ),
            "Medicine Full Text": (
                ".//a[contains(@title, 'Wolters Kluwer')]",
                call_medicine_script,
                By.CLASS_NAME,
                "ejp-article-title"
            ),
            "JASN Full Text": (
                ".//a[contains(@title, 'Wolters Kluwer')]",
                call_jasn_script,
                By.CLASS_NAME,
                "ejp-article-title"
            ),
            "PLOS ONE": (
                ".//a[contains(@href, 'dx.plos.org/')]",
                call_plosone_script,
                By.CSS_SELECTOR,
                "h1#artTitle"
            ),
            "J STAGE": (
                "//a[.//span[contains(text(), 'J-STAGE, Japan Science and Technology Information Aggregator, Electronic')]]",
                extract_jstage_info,
                By.CSS_SELECTOR,
                "div.global-article-title"
            ),
            "Hindawi": (
                ".//a[contains(@title, 'Hindawi Limited')]",
                call_hindawi_script,
                By.CSS_SELECTOR,
                "h1.citation__title"
            ),
            "Sage Journals": (
                ".//a[contains(@href, 'journals.sagepub.com/doi')]",
                call_sage_script,
                By.CSS_SELECTOR,
                "h1[property='name']"
            ),
            "Wiley": (
                ".//a[contains(@title, 'Wiley')]",
                call_wiley_script,
                By.CSS_SELECTOR,
                "h1.citation__title"
            ),
            "Mary Ann Liebert": (
                ".//a[contains(@href, 'liebertpub.com/doi')]",
                call_mary_ann_liebert_script,
                By.CSS_SELECTOR,
                "h1[property='name']"
            ),
            "Taylor Francis Online": (
                ".//a[contains(@href, 'tandfonline.com')]",
                call_taylor_francis_script,
                By.CSS_SELECTOR,
                "span.NLM_article-title"
            ),
            "Springer": (
                ".//a[contains(@title, 'See full text options at Springer')]",
                None,
                By.TAG_NAME,
                "h1"
            ),
            "Thieme Connect": (
                ".//a[contains(@title, 'See full text options at Georg Thieme Verlag Stuttgart, New York')]",
                extract_thieme_info,
                By.CSS_SELECTOR,
                "h1"
            ),
            "BioMed Central": (
                ".//a[contains(@title, 'BioMed Central')]",
                extract_bmc_info,
                By.CSS_SELECTOR,
                "h1.c-article-title"
            ),
            "Frontiers Media SA": (
                ".//a[contains(@title, 'Frontiers Media SA')]",
                extract_frontiers_info,
                By.CSS_SELECTOR,
                "h1"
            ),
            "Dove Medical Press": (
                ".//a[contains(@title, 'Dove Medical Press')]",
                extract_dovepress_info,
                By.CSS_SELECTOR,
                "h1"
            ),
            "American Chemical Society": (
                ".//a[contains(@title, 'American Chemical Society')]",
                extract_acs_info,
                By.CSS_SELECTOR,
                "h1.article_header-title > span.hlFld-Title"
            ),
            "IMR Press": (
                ".//a[contains(@title, 'IMR Press')]",
                extract_imr_press_info,
                By.CSS_SELECTOR,
                "div.ipubw-h1.mar-b-12.ipub-article-title.ipub-article-detail-title"
            ),
            "IOVS": (
                ".//a[contains(@title, 'Silverchair Information Systems')]",
                extract_iovs_info,
                By.CSS_SELECTOR,
                "h1"
            ),
            "Nature Publishing Group": (
                ".//a[contains(@title, 'Nature Publishing Group')]",
                extract_nature_portfolio_info,
                By.CSS_SELECTOR,
                "h1.c-article-title[data-test='article-title']"
            ),
            "Impact Journals, LLC": (
                ".//a[contains(@title, 'Impact Journals, LLC')]",
                extract_aging_info,
                By.CSS_SELECTOR,
                "h1#article-title"
            ),
            "Atypon": (
                ".//a[contains(@title, 'Atypon')]",
                extract_royal_society_info,
                By.CSS_SELECTOR,
                "h1.citation__title"
            ),
            "Oxford Academic": (
                ".//a[contains(@title, 'Silverchair Information Systems')]",
                extract_oxford_academic_info,
                By.CSS_SELECTOR,
                "h1.wi-article-title.article-title-main.accessible-content-title.at-articleTitle"
            )
        }


        for pub_name in scraper_map:
            if pub_name in available_choices and available_choices[pub_name] == True:
                print(f"Publisher found: {pub_name}")
                xpath_to_click, scraper_fn, wait_by, wait_selector = scraper_map[pub_name]

                clicked = click_button(driver, xpath_to_click)
                if not clicked:
                    return f"Failed to click the {pub_name} button."

                WebDriverWait(driver, 5).until(EC.number_of_windows_to_be(2))
                driver.switch_to.window(driver.window_handles[1])

                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((wait_by, wait_selector))
                    )
                except TimeoutException:
                    return f"Failed to find the required element '{wait_selector}' for {pub_name}."

                if scraper_fn is None:
                    return f"No specialized scraper implemented for {pub_name} yet."
                else:
                    raw_result = scraper_fn(driver)
                    if not raw_result or isinstance(raw_result, str):
                        return raw_result or f"Failed to extract {pub_name} info"


                final_result = {}
                final_result["title"] = raw_result.get("title", "No Title Found")
                authors_text = raw_result.get("author") or raw_result.get("authors") or "No authors"
                if authors_text and authors_text != "No authors":
                    final_result["first_author"] = authors_text.split(",")[0].strip()
                else:
                    final_result["first_author"] = "First author not available"


                final_result["full_text"] = raw_result.get("full_text", "No full text found")

                return final_result

        return "No recognized publisher function was invoked."

    except TimeoutException as e:
        print(f"TimeoutException encountered: {e}")
        return f"Timeout occurred: {e}"
    except WebDriverException as e:
        print(f"WebDriverException encountered: {e}")
        return f"WebDriver error: {e}"
    except Exception as e:
        print(f"An unexpected exception occurred in call_external_script: {e}")
        traceback.print_exc()
        return f"An error occurred: {e}"
    finally:
        if driver:
            driver.quit()


def pubmed_scrape(driver):
    """
    Original approach that tries to extract from 'pmc' page.
    """
    try:
        title_el = driver.find_element(By.TAG_NAME, "h1")
        title = title_el.text.strip()

        main_body = driver.find_element(By.CLASS_NAME, "main-article-body")
        full_text = main_body.text.strip()

        try:
            first_author_element = driver.find_element(By.CSS_SELECTOR, "div.cg.p a span.name.western")
            first_author = first_author_element.text.strip()
        except NoSuchElementException:
            first_author = "First author not available"

        return {
            "title": title,
            "author": first_author,
            "full_text": full_text
        }
    except Exception as e:
        print(f"Exception in pubmed_scrape: {e}")
        traceback.print_exc()
        return {}



def initialize_webdriver():
    """
    Initializes Chrome webdriver with basic options.
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    #options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    return driver


def check_buttons(driver, url):
    """
    Checks which publisher links are present on the PubMed (or related) page.
    Returns a dict of
      {
         'PubMed Central Free Full Text': True/False,
         'Elsevier Open Access': True/False,
         ...
      }
    """
    results = {
        "PubMed Central Free Full Text": ".//a[contains(@class, 'pmc')]",
        "Elsevier Open Access": ".//a[contains(@href, 'linkinghub.elsevier.com/retrieve/pii/')]",
        "CellPress Open Access": ".//a[contains(@href, 'linkinghub.elsevier.com/retrieve/pii/S2211-1247')]",
        "MDPI Full Text Open Access": ".//a[contains(@href, 'mdpi.com/resolver')]",
        "Medicine Full Text": ".//a[contains(@title, 'Wolters Kluwer')]",
        "JASN Full Text": ".//a[contains(@title, 'Wolters Kluwer')]",
        "PLOS ONE": ".//a[contains(@href, 'dx.plos.org/')]",
        "J STAGE": "//a[.//span[contains(text(), 'J-STAGE, Japan Science and Technology Information Aggregator, Electronic')]]",
        "Hindawi": ".//a[contains(@title, 'Hindawi Limited')]",
        "Sage Journals": ".//a[contains(@href, 'journals.sagepub.com/doi')]",
        "Wiley": ".//a[contains(@title, 'Wiley')]",
        "Mary Ann Liebert": ".//a[contains(@href, 'liebertpub.com/doi')]",
        "Taylor Francis Online": ".//a[contains(@href, 'tandfonline.com')]",
        "Springer": ".//a[contains(@title, 'See full text options at Springer')]",
        "Thieme Connect": ".//a[contains(@title, 'See full text options at Georg Thieme Verlag Stuttgart, New York')]",
        "BioMed Central": ".//a[contains(@title, 'BioMed Central')]",
        "Frontiers Media SA": ".//a[contains(@title, 'Frontiers Media SA')]",
        "Dove Medical Press": ".//a[contains(@title, 'Dove Medical Press')]",
        "American Chemical Society": ".//a[contains(@title, 'American Chemical Society')]",
        "IMR Press": ".//a[contains(@title, 'IMR Press')]",
        "IOVS": ".//a[contains(@title, 'Silverchair Information Systems')]",
        "Nature Publishing Group": ".//a[contains(@title, 'Nature Publishing Group')]",
        "Impact Journals, LLC": ".//a[contains(@title, 'Impact Journals, LLC')]",
        "Atypon": ".//a[contains(@title, 'Atypon')]",
        "Oxford Academic": ".//a[contains(@title, 'Silverchair Information Systems')]"
    }


    try:
        full_text_links = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "full-text-links-list"))
        )
        for key, xpath in results.items():
            try:
                full_text_links.find_element(By.XPATH, xpath)
                results[key] = True
            except NoSuchElementException:
                results[key] = False
    except (TimeoutException, NoSuchElementException):
        results = {key: False for key in results}

    return results


def click_button(driver, xpath):
    """
    Attempts to click a button/link via the given XPath.
    Returns True if successful, False otherwise.
    """
    try:
        button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        button.click()
        return True
    except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e:
        print(f"Error clicking button with XPath {xpath}: {e}")
        return False


def truncate_at_references(text):
    """
    Helper to chop off references or footnotes if found.
    """
    reference_phrases = [
        "Go to:\nDisclosures", "Go to:\nACKNOWLEDGMENTS", "Go to:\nAuthor Contributions",
        "Go to:\nAcknowledgments", "Go to:\nNotes", "Go to:\nACKNOWLEDGEMENT", "Go to:\nREFERENCES",
        "Go to:\nReferences", "Go to:\nFootnotes", "Go to:\nFunding"
    ]
    for phrase in reference_phrases:
        reference_index = text.find(phrase)
        if reference_index != -1:
            return text[:reference_index].strip()
    return text



def call_medicine_script(driver):
    """
    Example: Wolters Kluwer (Medicine Full Text) approach
    """
    extracted_info = extract_medicine_info(driver)
    if not extracted_info:
        return "Failed to extract information from the page."

    full_text = extract_full_text(driver, "ArticleBody")

    return {**extracted_info, "full_text": full_text}


def call_jasn_script(driver):
    """
    JASN Full Text approach (also Wolters Kluwer)
    """
    extracted_info = extract_medicine_info(driver)
    if not extracted_info:
        return "Failed to extract information from the page."

    full_text = extract_full_text(driver, "ArticleBody")
    return {**extracted_info, "full_text": full_text}


def extract_medicine_info(driver):
    """
    For Wolters Kluwer / Medicine / JASN
    """
    try:
        title = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ejp-article-title"))
        ).text
        authors = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "ejp-article-authors"))
        ).text
        authors = authors.replace('Author Information', '').strip()
        abstract = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "abstractWrap"))
        ).text.strip()

        return {"title": title, "authors": authors, "abstract": abstract}
    except (NoSuchElementException, TimeoutException) as e:
        print(f"Error extracting medicine info: {e}")
        traceback.print_exc()
        return None


def extract_full_text(driver, content_id):
    """
    Wait for content_id to appear, then return its .text
    """
    try:
        content_div = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, content_id))
        )
        return content_div.text
    except (NoSuchElementException, TimeoutException) as e:
        print(f"Error extracting full text: {e}")
        traceback.print_exc()
        return None


def call_mdpi_script(driver):
    extracted_info = extract_mdpi_info(driver)
    if not extracted_info:
        return "Failed to extract information from the page."

    full_text = extract_mdpi_full_text(driver)

    return {
        "title": extracted_info["title"],
        "authors": extracted_info["authors"],
        "abstract": extracted_info["abstract"],
        "full_text": full_text
    }


def extract_mdpi_info(driver):
    try:
        title = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1.title.hypothesis_container"))
        ).text
        authors_elements = driver.find_elements(By.CSS_SELECTOR,
                                                ".art-authors.hypothesis_container .inlineblock .profile-card-drop")
        authors = ', '.join([a.text for a in authors_elements])
        abstract = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#html-abstract .html-p"))
        ).text.strip()

        return {
            "title": title,
            "authors": authors,
            "abstract": abstract
        }
    except (NoSuchElementException, TimeoutException) as e:
        print(f"Error extracting MDPI info: {e}")
        traceback.print_exc()
        return None


def extract_mdpi_full_text(driver):
    try:
        content_div = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".html-body"))
        )
        return content_div.text
    except (NoSuchElementException, TimeoutException) as e:
        print(f"Error extracting full text: {e}")
        traceback.print_exc()
        return None


def call_elsevier_script(driver):
    extracted_info = extract_elsevier_info(driver)
    if not extracted_info:
        return "Failed to extract information from the page."

    full_text = extract_elsevier_full_text(driver)
    return {
        "title": extracted_info["title"],
        "authors": extracted_info["authors"],
        "abstract": extracted_info["abstract"],
        "full_text": full_text
    }


def extract_elsevier_info(driver):
    try:
        title = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.title-text"))
        ).text
        authors_elems = WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".AuthorGroups .author-group .button-link-text"))
        )
        authors = ", ".join(a.text for a in authors_elems)
        abstract = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".abstract.author"))
        ).text.strip()

        return {
            "title": title,
            "authors": authors,
            "abstract": abstract
        }
    except (NoSuchElementException, TimeoutException) as e:
        print(f"Error extracting Elsevier info: {e}")
        traceback.print_exc()
        return None
    except Exception as e:
        print(f"Unexpected error in extract_elsevier_info: {e}")
        traceback.print_exc()
        return None


def extract_elsevier_full_text(driver):
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.TAG_NAME, "article"))
        )
        content_div = driver.find_element(By.TAG_NAME, "article")
        return content_div.text
    except (NoSuchElementException, TimeoutException) as e:
        print(f"Error extracting elsevier full text: {e}")
        traceback.print_exc()
        return None


def call_plosone_script(driver):
    extracted_info = extract_plosone_info(driver)
    if not extracted_info:
        return "Failed to extract information from the page."

    full_text = extract_plosone_full_text(driver)
    return {
        "title": extracted_info["title"],
        "authors": extracted_info["authors"],
        "abstract": extracted_info["abstract"],
        "full_text": full_text
    }


def extract_plosone_info(driver):
    try:
        title = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1#artTitle"))
        ).text
        authors_elems = driver.find_elements(By.CSS_SELECTOR, ".author-list .author-name")
        authors = ", ".join(a.text for a in authors_elems)
        abstract = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.abstract"))
        ).text.strip()

        return {
            "title": title,
            "authors": authors,
            "abstract": abstract
        }
    except (NoSuchElementException, TimeoutException) as e:
        print(f"Error extracting PLOS ONE info: {e}")
        traceback.print_exc()
        return None


def extract_plosone_full_text(driver):
    try:
        sections = driver.find_elements(By.CSS_SELECTOR, "div.section.toc-section")
        full_text = "\n\n".join([sec.text for sec in sections])
        return full_text
    except (NoSuchElementException, TimeoutException) as e:
        print(f"Error extracting plos one full text: {e}")
        traceback.print_exc()
        return None


def call_mary_ann_liebert_script(driver):
    extracted_info = extract_mary_ann_liebert_info(driver)
    if not extracted_info:
        return "Failed to extract information from the page."

    full_text = extract_full_text_using_js(driver)
    return {
        "title": extracted_info["title"],
        "authors": extracted_info["authors"],
        "abstract": extracted_info["abstract"],
        "full_text": full_text
    }


def extract_mary_ann_liebert_info(driver):
    try:
        title = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1[property='name']"))
        ).text
        author_elems = driver.find_elements(By.CSS_SELECTOR, "span[role='list'] > span")
        authors = ", ".join(a.text for a in author_elems)
        abstract = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "section#abstract"))
        ).text.strip()

        return {
            "title": title,
            "authors": authors,
            "abstract": abstract
        }
    except (NoSuchElementException, TimeoutException) as e:
        print(f"Error extracting Mary Ann Liebert info: {e}")
        traceback.print_exc()
        return None


def extract_full_text_using_js(driver):
    try:
        full_text = driver.execute_script("""
            let fullText = "";
            const coreContainer = document.querySelector("section#bodymatter .core-container");
            if (coreContainer) {
                const sections = coreContainer.querySelectorAll("section");
                sections.forEach(section => {
                    fullText += section.innerText + "\\n\\n";
                });
            }
            return fullText.trim();
        """)
        return full_text
    except WebDriverException as e:
        print(f"Error executing JavaScript for full text extraction: {e}")
        traceback.print_exc()
        return None


def call_wiley_script(driver):
    extracted_info = extract_wiley_info(driver)
    if not extracted_info:
        return "Failed to extract information from the page."

    full_text = extract_wiley_full_text(driver)
    result = {
        "title": extracted_info["title"],
        "authors": extracted_info["authors"],
        "abstract": extracted_info["abstract"]
    }
    if full_text:
        result["full_text"] = full_text
    return result


def extract_wiley_info(driver):
    try:
        title = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1.citation__title"))
        ).text
        authors_elems = driver.find_elements(By.CSS_SELECTOR, "div.accordion-tabbed")
        authors = ", ".join([elem.text for elem in authors_elems])
        abstract = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.abstract-group.metis-abstract"))
        ).text.strip()

        return {
            "title": title,
            "authors": authors,
            "abstract": abstract
        }
    except (NoSuchElementException, TimeoutException) as e:
        print(f"Error extracting Wiley info: {e}")
        traceback.print_exc()
        return None


def extract_wiley_full_text(driver):
    try:
        full_text = driver.execute_script("""
            let fullText = "";
            const articleSections = document.querySelectorAll("section.article-section.article-section__full");
            if (articleSections) {
                articleSections.forEach(section => {
                    fullText += section.innerText + "\\n\\n";
                });
            }
            return fullText.trim();
        """)
        return full_text if full_text else None
    except WebDriverException as e:
        print(f"Error executing JavaScript for wiley full text: {e}")
        traceback.print_exc()
        return None


def call_sage_script(driver):
    extracted_info = extract_sage_info(driver)
    if not extracted_info:
        return "Failed to extract information from the page."

    full_text = extract_sage_full_text(driver)
    result = {
        "title": extracted_info["title"],
        "authors": extracted_info["authors"],
        "abstract": extracted_info["abstract"]
    }
    if full_text:
        result["full_text"] = full_text
    return result


def extract_sage_info(driver):
    try:
        title = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1[property='name']"))
        ).text
        authors_elems = driver.find_elements(By.CSS_SELECTOR, "span[role='list']")
        authors = ", ".join([a.text for a in authors_elems])
        abstract = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "section#abstract[property='abstract']"))
        ).text.strip()

        return {
            "title": title,
            "authors": authors,
            "abstract": abstract
        }
    except (NoSuchElementException, TimeoutException) as e:
        print(f"Error extracting Sage info: {e}")
        traceback.print_exc()
        return None


def extract_sage_full_text(driver):
    try:
        full_text = driver.execute_script("""
            let fullText = "";
            const articleSections = document.querySelectorAll("section#bodymatter[data-extent='bodymatter'] .core-container > section");
            if (articleSections.length) {
                articleSections.forEach(section => {
                    fullText += section.innerText + "\\n\\n";
                });
            }
            return fullText.trim();
        """)
        return full_text if full_text else None
    except WebDriverException as e:
        print(f"Error executing JavaScript for sage full text: {e}")
        traceback.print_exc()
        return None


def call_hindawi_script(driver):
    extracted_info = extract_hindawi_info(driver)
    if not extracted_info or not isinstance(extracted_info, dict):
        return "Failed to extract information from the page."
    return extracted_info


def extract_hindawi_info(driver):
    """
    Hindawi structure. If it's a more modern layout, might differ. Adjust as needed.
    """
    result = {}
    try:
        try:
            result["title"] = driver.find_element(By.CSS_SELECTOR, "h1.citation__title").text
        except NoSuchElementException:
            result["title"] = "Title not found"

        try:
            author_section = driver.find_element(By.CSS_SELECTOR, "div.accordion-tabbed")
            result["authors"] = author_section.text
        except NoSuchElementException:
            result["authors"] = "Author not found"

        try:
            abstract_section = driver.find_element(By.CSS_SELECTOR, "section.article-section.article-section__abstract")
            result["abstract"] = abstract_section.text
        except NoSuchElementException:
            result["abstract"] = "Abstract not found"

        try:
            full_text_section = driver.find_element(By.CSS_SELECTOR, "section.article-section.article-section__full")
            result["full_text"] = full_text_section.text
        except NoSuchElementException:
            result["full_text"] = "Full text not found"
    except Exception as e:
        print(f"Error extracting Hindawi info: {e}")
        traceback.print_exc()
        return None

    return result


def extract_jstage_info(driver):
    """
    Steps:
     - Possibly click "Full-text HTML" inside J-STAGE after switching windows
    """
    try:
        title = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.global-article-title"))
        ).text
        authors = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.global-authors-name-tags"))
        ).text
        abstract = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div#article-overiew-abstract-wrap"))
        ).text.strip()

        click_jstage_full_text(driver)

        full_text_sections = driver.find_elements(By.CSS_SELECTOR, "div.non-sticky-content > div[id^='sec']")
        full_text = "\n".join([section.text for section in full_text_sections])

        return {
            "title": title,
            "authors": authors,
            "abstract": abstract,
            "full_text": full_text
        }
    except (NoSuchElementException, TimeoutException) as e:
        print(f"Error extracting J-STAGE info: {e}")
        return None


def click_jstage_full_text(driver):
    """
    After switching to the J-STAGE window, tries to click "Full-text HTML".
    """
    try:
        full_text_link = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.thirdlevel-active-btn"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", full_text_link)
        driver.execute_script("arguments[0].click();", full_text_link)
        return True
    except Exception as e:
        print(f"Error clicking J-STAGE full-text button: {e}")
        return False


def call_taylor_francis_script(driver):
    try:
        title_element = driver.find_element(By.CSS_SELECTOR, "span.NLM_article-title.hlFld-title")
        author_element = driver.find_element(By.CSS_SELECTOR, "span.NLM_contrib-group")
        abstract_element = driver.find_element(By.CSS_SELECTOR, "div.hlFld-Abstract")
        full_text_element = driver.find_element(By.CSS_SELECTOR, "div.hlFld-Fulltext")

        return {
            "title": title_element.text,
            "authors": author_element.text,
            "abstract": abstract_element.text,
            "full_text": full_text_element.text
        }
    except Exception as e:
        print(f"Error extracting Taylor Francis Online info: {e}")
        return None


def extract_thieme_info(driver):
    """
    Georg Thieme Verlag scraping approach.
    """
    try:
        WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1")))
        try:
            cookie_reject_button = driver.find_element(By.ID, "onetrust-reject-all-handler")
            cookie_reject_button.click()
            print("Rejected cookies.")
        except NoSuchElementException:
            pass

        title_element = driver.find_element(By.CSS_SELECTOR, "h1")
        title = title_element.text

        author_element = driver.find_element(By.CSS_SELECTOR, "span.author")
        author = author_element.text

        abstract_element = driver.find_element(By.CSS_SELECTOR, "section#abstract")
        abstract = abstract_element.text

        ul_element = driver.find_element(By.ID, "articleTabs")
        ul_html = ul_element.get_attribute('outerHTML')
        soup = BeautifulSoup(ul_html, 'html.parser')
        li_elements = soup.find_all('li')

        volltext_button = soup.find('a', href=True, text='Volltext')
        if volltext_button:
            volltext_url = f"https://www.thieme-connect.com{volltext_button['href']}"
            driver.get(volltext_url)
            try:
                full_text_element = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.ID, "htmlfulltext"))
                )
                full_text = full_text_element.text
            except TimeoutException:
                full_text = ""
        else:
            print("Volltext button not found.")
            full_text = ""

        return {"title": title, "author": author, "abstract": abstract, "full_text": full_text}
    except Exception as e:
        print(f"Error extracting Thieme info: {str(e)}")
        return {}


def extract_bmc_info(driver):
    """
    BioMed Central approach
    """
    try:
        title = driver.find_element(By.CSS_SELECTOR, "h1.c-article-title").text
        author_elems = driver.find_elements(By.CSS_SELECTOR, "ul.c-article-author-list li")
        authors = ', '.join([a.text for a in author_elems])
        abstract = driver.find_element(By.CSS_SELECTOR, "div#Abs1-section").text
        full_text_element = driver.find_element(By.CSS_SELECTOR, "article")
        full_text = full_text_element.text

        return {
            "title": title,
            "authors": authors,
            "abstract": abstract,
            "full_text": full_text
        }
    except Exception as e:
        print(f"Error extracting BMC info: {e}")
        return {}


def extract_frontiers_info(driver):
    """
    Frontiers Media approach
    """
    try:
        title = driver.find_element(By.CSS_SELECTOR, "h1").text
        authors = driver.find_element(By.CSS_SELECTOR, "div.authors").text
        abstract = driver.find_element(By.CSS_SELECTOR, "div.JournalAbstract").text
        full_text_element = driver.find_element(By.CSS_SELECTOR, "div.JournalFullText")
        full_text = full_text_element.text
        return {
            "title": title,
            "authors": authors,
            "abstract": abstract,
            "full_text": full_text
        }
    except Exception as e:
        print(f"Error extracting Frontiers info: {e}")
        return {}


def extract_dovepress_info(driver):
    """
    Dove Medical Press
    """
    result = {}
    try:
        title = driver.find_element(By.CSS_SELECTOR, "h1").text
        result["title"] = title
    except NoSuchElementException:
        result["title"] = "Title not found"
    try:
        author_section = driver.find_element(By.CSS_SELECTOR, "div.padding > p")
        result["authors"] = author_section.text
    except NoSuchElementException:
        result["authors"] = "Author not found"
    try:
        abstract_section = driver.find_element(By.CSS_SELECTOR, "div.article-inner_html > p")
        result["abstract"] = abstract_section.text
    except NoSuchElementException:
        result["abstract"] = "Abstract not found"
    try:
        full_text_section = driver.find_element(By.CSS_SELECTOR, "div#article-fulltext")
        result["full_text"] = full_text_section.text
    except NoSuchElementException:
        result["full_text"] = "Full text not found"
    return result


def extract_acs_info(driver):
    """
    American Chemical Society
    """
    result = {}
    try:
        title = driver.find_element(By.CSS_SELECTOR, "h1.article_header-title > span.hlFld-Title").text
        result["title"] = title
    except NoSuchElementException:
        result["title"] = "Title not found"
    try:
        author_section = driver.find_element(By.CSS_SELECTOR, "ul.loa")
        result["authors"] = author_section.text
    except NoSuchElementException:
        result["authors"] = "Author not found"
    try:
        abstract_section = driver.find_element(By.CSS_SELECTOR, "p.articleBody_abstractText")
        result["abstract"] = abstract_section.text
    except NoSuchElementException:
        result["abstract"] = "Abstract not found"
    try:
        full_text_section = driver.find_element(By.CSS_SELECTOR, "div.article_content-left.ui-resizable")
        result["full_text"] = full_text_section.text
    except NoSuchElementException:
        result["full_text"] = "Full text not found"
    return result


def extract_imr_press_info(driver):
    """
    IMR Press
    """
    result = {}
    try:
        title = driver.find_element(By.CSS_SELECTOR,
                                    "div.ipubw-h1.mar-b-12.ipub-article-title.ipub-article-detail-title").text
        result["title"] = title
    except NoSuchElementException:
        result["title"] = "Title not found"

    try:
        author_section = driver.find_element(By.CSS_SELECTOR, "div.ipubw-p3.mar-b-12.font-color")
        result["authors"] = author_section.text
    except NoSuchElementException:
        result["authors"] = "Author not found"

    try:
        abstract_section = driver.find_element(By.CSS_SELECTOR,
                                               "div.ipubw-p3.font-color.ipub-abstract.ipub-html-full-text")
        result["abstract"] = abstract_section.text
    except NoSuchElementException:
        result["abstract"] = "Abstract not found"

    try:
        view_btn = driver.find_element(By.XPATH, "//a[contains(@href, '/htm')]/div")
        view_btn.click()
        full_text_section = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.mar-b-40.ipub-html-content.ipub-html-full-text"))
        )
        result["full_text"] = full_text_section.text
    except (NoSuchElementException, TimeoutException):
        result["full_text"] = "Full text not found"

    return result


def extract_iovs_info(driver):
    """
    IOVS (Silverchair)
    """
    result = {}
    try:
        title = driver.find_element(By.CSS_SELECTOR, "div.wi-article-title.article-title-main").text
        result["title"] = title
    except NoSuchElementException:
        result["title"] = "Title not found"

    try:
        author_section = driver.find_element(By.CSS_SELECTOR, "div.al-authors-list")
        result["authors"] = author_section.text
    except NoSuchElementException:
        result["authors"] = "Author not found"

    try:
        abstract_section = driver.find_element(By.CSS_SELECTOR, "section.abstract")
        result["abstract"] = abstract_section.text
    except NoSuchElementException:
        result["abstract"] = "Abstract not found"

    try:
        full_text_section = driver.find_element(By.CSS_SELECTOR, "div.widget-items[data-widgetname='ArticleFulltext']")
        result["full_text"] = full_text_section.text
    except NoSuchElementException:
        result["full_text"] = "Full text not found"

    return result


def extract_nature_portfolio_info(driver):
    result = {}
    try:
        title = driver.find_element(By.CSS_SELECTOR, "h1.c-article-title[data-test='article-title']").text
        result["title"] = title
    except NoSuchElementException:
        result["title"] = "Title not found"

    try:
        author_section = driver.find_element(By.CSS_SELECTOR, "ul.c-article-author-list[data-test='authors-list']")
        result["authors"] = author_section.text
    except NoSuchElementException:
        result["authors"] = "Author not found"

    try:
        abstract_section = driver.find_element(By.CSS_SELECTOR, "div.c-article-section#Abs1-section")
        result["abstract"] = abstract_section.text
    except NoSuchElementException:
        result["abstract"] = "Abstract not found"

    try:
        full_text_section = driver.find_element(By.CSS_SELECTOR, "div.main-content")
        result["full_text"] = full_text_section.text
    except NoSuchElementException:
        result["full_text"] = "Full text not found"

    return result


def extract_aging_info(driver):
    """
    Impact Journals, LLC (Aging)
    """
    try:
        title = driver.find_element(By.CSS_SELECTOR, "h1#article-title").text
        author = driver.find_element(By.CSS_SELECTOR, "h4.authors").text
        abstract = driver.find_element(By.CSS_SELECTOR, "div.abstract.article-text").text
        section_containers = driver.find_elements(By.CSS_SELECTOR, "div.section-container")
        full_text = "\n".join([sec.text for sec in section_containers])

        return {
            'title': title,
            'authors': author,
            'abstract': abstract,
            'full_text': full_text
        }
    except Exception as e:
        print(f"Error extracting Aging info: {str(e)}")
        return {}


def extract_royal_society_info(driver):
    """
    Atypon
    """
    try:
        title = driver.find_element(By.CSS_SELECTOR, "h1.citation__title").text
        author = driver.find_element(By.CSS_SELECTOR, "div.accordion-tabbed.loa-accordion").text
        abstract = driver.find_element(By.CSS_SELECTOR, "div.abstractSection.abstractInFull").text
        full_text = driver.find_element(By.CSS_SELECTOR, "div.hlFld-Fulltext").text
        return {
            'title': title,
            'authors': author,
            'abstract': abstract,
            'full_text': full_text
        }
    except Exception as e:
        print(f"Error extracting Royal Society info: {str(e)}")
        return {}


def extract_oxford_academic_info(driver):
    try:
        title = driver.find_element(By.CSS_SELECTOR,
                                    "h1.wi-article-title.article-title-main.accessible-content-title.at-articleTitle").text
    except:
        title = "Title not found"

    try:
        author = driver.find_element(By.CSS_SELECTOR, "div.al-authors-list").text
    except:
        author = "Author not found"

    try:
        abstract = driver.find_element(By.CSS_SELECTOR, "section.abstract").text
    except:
        abstract = "Abstract not found"

    try:
        full_text = driver.find_element(By.CSS_SELECTOR, "div.widget-items[data-widgetname='ArticleFulltext']").text
    except:
        full_text = "Full text not found"

    return {
        "title": title,
        "authors": author,
        "abstract": abstract,
        "full_text": full_text
    }


if __name__ == "__main__":
    print("Starting Flask app on port 5003.")
    app.run(port=80)
