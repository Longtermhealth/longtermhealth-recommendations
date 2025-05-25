"""Health Score Service - Business logic for health score calculations"""

import math
import logging
from typing import Dict, Any, List, Optional

from src.utils.strapi_api import strapi_get_health_scores

logger = logging.getLogger(__name__)

# Constants
K_FACTOR = 0.025

# Score interpretation mappings
SCORE_INTERPRETATIONS = {
    "MOVEMENT": {
        "AKTIONSBEFARF": "Es ist Zeit, mehr Bewegung in deinen Alltag zu integrieren. Kleine Schritte können einen großen Unterschied für deine Gesundheit machen!",
        "AUSBAUFÄHIG": "Deine körperliche Aktivität ist gut! Mit ein wenig mehr Bewegung kannst du deine Fitness auf das nächste Level heben.",
        "OPTIMAL": "Fantastische Leistung! Deine regelmäßige Bewegung stärkt deine Gesundheit optimal. Weiter so!"
    },
    "NUTRITION": {
        "AKTIONSBEFARF": "Achte mehr auf eine ausgewogene Ernährung. Gesunde Essgewohnheiten geben dir Energie und Wohlbefinden.",
        "AUSBAUFÄHIG": "Deine Ernährung ist auf einem guten Weg! Mit kleinen Anpassungen kannst du deine Nährstoffzufuhr weiter optimieren.",
        "OPTIMAL": "Exzellente Ernährungsgewohnheiten! Du versorgst deinen Körper optimal mit wichtigen Nährstoffen. Weiter so!"
    },
    "SLEEP": {
        "AKTIONSBEFARF": "Verbessere deine Schlafgewohnheiten für mehr Energie und bessere Gesundheit. Guter Schlaf ist essenziell!",
        "AUSBAUFÄHIG": "Dein Schlaf ist gut! Ein paar Änderungen können dir helfen, noch erholsamer zu schlafen.",
        "OPTIMAL": "Ausgezeichneter Schlaf! Du sorgst für optimale Erholung und Vitalität. Weiter so!"
    },
    "SOCIAL_ENGAGEMENT": {
        "AKTIONSBEFARF": "Pflege deine sozialen Beziehungen. Verbindungen zu anderen sind wichtig für dein emotionales Wohlbefinden.",
        "AUSBAUFÄHIG": "Deine sozialen Beziehungen sind gut! Mit ein wenig mehr Engagement kannst du deine Verbindungen weiter vertiefen.",
        "OPTIMAL": "Starke und erfüllende soziale Beziehungen! Du pflegst wertvolle Verbindungen, die dein Leben bereichern. Weiter so!"
    },
    "STRESS": {
        "AKTIONSBEFARF": "Es ist wichtig, Wege zu finden, um deinen Stress besser zu bewältigen. Kleine Pausen und Entspannungstechniken können helfen.",
        "AUSBAUFÄHIG": "Dein Umgang mit Stress ist gut! Mit weiteren Strategien kannst du deine Stressresistenz weiter stärken.",
        "OPTIMAL": "Du meisterst Stress hervorragend! Deine effektiven Bewältigungsstrategien tragen zu deinem Wohlbefinden bei. Weiter so!"
    },
    "GRATITUDE": {
        "AKTIONSBEFARF": "Nimm dir Zeit, die positiven Dinge im Leben zu schätzen. Dankbarkeit kann dein Wohlbefinden erheblich steigern.",
        "AUSBAUFÄHIG": "Du zeigst bereits Dankbarkeit! Mit kleinen Ergänzungen kannst du deine positive Einstellung noch weiter ausbauen.",
        "OPTIMAL": "Eine wunderbare Haltung der Dankbarkeit! Deine positive Sicht bereichert dein Leben und das deiner Mitmenschen. Weiter so!"
    },
    "COGNITIVE_ENHANCEMENT": {
        "AKTIONSBEFARF": "Fordere deinen Geist regelmäßig heraus. Neue Lernmöglichkeiten können deine geistige Fitness verbessern.",
        "AUSBAUFÄHIG": "Deine kognitive Förderung ist gut! Mit zusätzlichen Aktivitäten kannst du deine geistige Leistungsfähigkeit weiter steigern.",
        "OPTIMAL": "Hervorragende geistige Fitness! Du hältst deinen Verstand aktiv und stark. Weiter so!"
    }
}


class HealthScoreService:
    """Service for calculating and managing health scores"""
    
    @staticmethod
    def compute_routine_completion(routine: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute completion statistics for a routine.
        
        Returns:
            Dict with scheduled, completed, and percentage
        """
        stats = routine.get("completionStatistics", [])
        if not stats:
            return {"scheduled": 0, "completed": 0, "percentage": None}
        
        actual_rates = [int(stat.get("completionRate", 0)) for stat in stats]
        scheduled = len(actual_rates)
        completed = sum(actual_rates)
        
        # Calculate expected total
        unique_rates = set(actual_rates)
        if len(unique_rates) == 1:
            expected_total = unique_rates.pop() * scheduled
        else:
            expected_total = 0
            for stat in stats:
                unit = stat.get("completionRatePeriodUnit")
                try:
                    seq = int(stat.get("periodSequenceNo", 0))
                except (ValueError, TypeError):
                    seq = 0
                
                if unit == "WEEK":
                    expected_total += min(seq, 4)
                elif unit == "MONTH":
                    expected_total += 4
                else:
                    expected_total += int(stat.get("completionRate", 0))
        
        percentage = (completed / expected_total * 100) if expected_total > 0 else 0
        
        return {
            "scheduled": scheduled,
            "completed": completed,
            "percentage": percentage
        }
    
    @staticmethod
    def get_insights(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate insights from pillar completion statistics.
        """
        insights = {}
        
        for pillar in payload.get("pillarCompletionStats", []):
            pillar_name = pillar.get("pillarEnum")
            routines = pillar.get("routineCompletionStats", [])
            routine_details = []
            
            for routine in routines:
                completion_stats = HealthScoreService.compute_routine_completion(routine)
                rates = [int(stat.get("completionRate", 0)) 
                        for stat in routine.get("completionStatistics", [])]
                avg_rate = sum(rates) / len(rates) if rates else None
                
                detail = {
                    "routineId": routine.get("routineId"),
                    "displayName": routine.get("displayName"),
                    "scheduled": completion_stats["scheduled"],
                    "completed": completion_stats["completed"],
                    "completionPercentage": completion_stats["percentage"],
                    "averageCompletionRate": avg_rate,
                    "numStatistics": len(routine.get("completionStatistics", []))
                }
                routine_details.append(detail)
            
            insights[pillar_name] = {
                "numRoutines": len(routines),
                "routines": routine_details
            }
        
        return insights
    
    @staticmethod
    def get_score_rating(score: float) -> str:
        """Determine rating based on score"""
        if score < 40:
            return "AKTIONSBEFARF"
        elif 40 <= score < 64:
            return "AUSBAUFÄHIG"
        else:
            return "OPTIMAL"
    
    @staticmethod
    def get_score_details(pillar: str, score: float) -> Dict[str, str]:
        """Get detailed score information including interpretation"""
        rating = HealthScoreService.get_score_rating(score)
        return {
            "ratingEnum": rating,
            "displayName": rating.capitalize(),
            "scoreInterpretation": SCORE_INTERPRETATIONS.get(pillar, {}).get(
                rating, 
                "No interpretation available."
            )
        }
    
    @staticmethod
    def create_health_scores_structure(account_id: int, health_scores: Dict[str, float]) -> Dict[str, Any]:
        """
        Build the final health-scores structure to post to Strapi.
        """
        if not isinstance(health_scores, dict) or not health_scores:
            logger.error(f"Empty or invalid health_scores for account {account_id}")
            return {
                "data": {
                    "totalScore": 0,
                    "accountId": account_id,
                    "pillarScores": []
                }
            }
        
        total_score = sum(health_scores.values()) / len(health_scores)
        pillars = []
        
        for pillar_enum, score in health_scores.items():
            details = HealthScoreService.get_score_details(pillar_enum, score)
            pillars.append({
                "pillar": {
                    "pillarEnum": pillar_enum,
                    "displayName": pillar_enum.replace("_", " ").capitalize()
                },
                "score": f"{score:.2f}",
                "scoreInterpretation": details["scoreInterpretation"],
                "rating": {
                    "ratingEnum": details["ratingEnum"],
                    "displayName": details["displayName"]
                }
            })
        
        return {
            "data": {
                "totalScore": int(total_score),
                "accountId": account_id,
                "pillarScores": pillars
            }
        }
    
    @staticmethod
    def compute_scheduled_by_pillar(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract scheduled routines grouped by pillar from different payload formats.
        """
        scheduled_by_pillar = {}
        
        # Handle webhook payload format
        if "pillarCompletionStats" in payload:
            for pillar in payload["pillarCompletionStats"]:
                pillar_enum = pillar.get("pillarEnum")
                routines = pillar.get("routineCompletionStats", [])
                scheduled_by_pillar[pillar_enum] = routines
        else:
            # Handle Strapi payload format
            data = payload.get("data", [])
            if isinstance(data, list) and data:
                attributes = data[0].get("attributes", {})
                routines_list = attributes.get("routines", [])
                
                for routine in routines_list:
                    pillar_enum = routine.get("pillar", {}).get("pillarEnum")
                    scheduled_by_pillar.setdefault(pillar_enum, []).append(routine)
        
        return scheduled_by_pillar
    
    @staticmethod
    def extract_completions_by_pillar(payload: Dict[str, Any]) -> Dict[str, Dict[str, int]]:
        """
        Extract completed counts from payload and sum them by pillar.
        """
        completions_by_pillar = {}
        
        for pillar_entry in payload.get("pillarCompletionStats", []):
            pillar = pillar_entry.get("pillarEnum", "UNKNOWN")
            if pillar not in completions_by_pillar:
                completions_by_pillar[pillar] = {"completed": 0}
            
            for routine in pillar_entry.get("routineCompletionStats", []):
                # Filter for MONTH statistics
                month_stats = [
                    stat for stat in routine.get("completionStatistics", [])
                    if stat.get("completionRatePeriodUnit") == "MONTH"
                ]
                
                if month_stats:
                    # Get the latest month entry
                    latest_stat = max(month_stats, key=lambda s: s.get("periodSequenceNo", 0))
                    completion = latest_stat.get("completionRate", 0)
                else:
                    completion = 0
                
                completions_by_pillar[pillar]["completed"] += completion
        
        return completions_by_pillar
    
    @staticmethod
    def calculate_first_month_update(
        account_id: int, 
        action_plan: Dict[str, Any], 
        pretty_payload: Dict[str, Any], 
        initial_health_scores: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Calculate health score updates based on first month completion data.
        """
        logger.info(f"Calculating first month update for account {account_id}")
        
        if action_plan is None:
            logger.error(f"No action_plan for account {account_id}")
            return {}
        
        # Get scheduled routines by pillar
        scheduled_by_pillar = HealthScoreService.compute_scheduled_by_pillar(action_plan)
        
        # Get completions by pillar
        completions_by_pillar = HealthScoreService.extract_completions_by_pillar(pretty_payload)
        
        final_scores = {}
        final_deltas = {}
        
        for pillar, info in scheduled_by_pillar.items():
            # Determine scheduled total
            if isinstance(info, dict) and "scheduled" in info:
                scheduled_total = info["scheduled"]
            elif isinstance(info, list):
                scheduled_total = len(info)
            else:
                scheduled_total = 0
            
            completed_count = completions_by_pillar.get(pillar, {}).get("completed", 0)
            not_completed_count = scheduled_total - completed_count
            
            # Calculate score delta
            init_score = initial_health_scores.get(pillar, 50)
            dampening = (100 - init_score) / 90.0
            
            delta_completed = 10 * dampening * (1 - math.exp(-K_FACTOR * completed_count))
            delta_not = 10 * dampening * (1 - math.exp(-K_FACTOR * not_completed_count))
            final_delta = delta_completed - (delta_not / 3.0)
            
            # Calculate new score
            new_score = init_score + final_delta
            new_score = min(max(new_score, 0), 100)
            
            final_scores[pillar] = new_score
            final_deltas[pillar] = final_delta
            
            logger.info(
                f"{pillar}: scheduled={scheduled_total}, completed={completed_count}, "
                f"not_completed={not_completed_count}, delta={final_delta:.4f}, "
                f"new_score={new_score:.4f}"
            )
        
        # Create final structure
        base_structure = HealthScoreService.create_health_scores_structure(account_id, final_scores)
        
        # Add deltas to the structure
        for entry in base_structure["data"]["pillarScores"]:
            pillar = entry["pillar"]["pillarEnum"]
            entry["delta"] = round(final_deltas.get(pillar, 0), 2)
        
        return base_structure