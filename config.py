# rule_based_system/config.py

from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    CLICKUP_API_KEY = os.getenv("CLICKUP_API_KEY")
    CLICKUP_LIST_ID = os.getenv("CLICKUP_LIST_ID")
    SCORES_FIELD_ID = os.getenv("SCORES_FIELD_ID")
    PLOT_FIELD_ID = os.getenv("PLOT_FIELD_ID")
    ANSWERS_FIELD_ID = os.getenv("ANSWERS_FIELD_ID")
    ROUTINES_FIELD_ID = os.getenv("ROUTINES_FIELD_ID")
    ACTIONPLAN_FIELD_ID = os.getenv("ACTIONPLAN_FIELD_ID")
    TYPEFORM_API_KEY = os.getenv("TYPEFORM_API_KEY")
    FORM_ID = os.getenv("FORM_ID")
    LINK_SUMMARY_TITLE_FIELD_ID = os.getenv("LINK_SUMMARY_TITLE_FIELD_ID")
    LINK_SUMMARY_SUMMARY_FIELD_ID = os.getenv("LINK_SUMMARY_SUMMARY_FIELD_ID")
    LINK_SUMMARY_OPENAI_API_KEY = os.getenv("LINK_SUMMARY_OPENAI_API_KEY")