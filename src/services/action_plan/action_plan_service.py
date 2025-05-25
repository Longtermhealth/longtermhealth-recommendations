"""Action Plan Service - Business logic for action plan operations"""

import json
import uuid
import logging
from typing import Dict, Any, List, Optional, Tuple

from src.utils.strapi_api import (
    strapi_get_old_action_plan,
    strapi_post_action_plan
)

logger = logging.getLogger(__name__)


class ActionPlanService:
    """Service for handling action plan operations"""
    
    @staticmethod
    def print_matching_routine_details(new_data: Dict[str, Any], old_action_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find matching routines between new data and old action plan.
        
        Args:
            new_data: New payload data with pillarCompletionStats
            old_action_plan: Existing action plan from Strapi
            
        Returns:
            List of matching routines with their details
        """
        old_routines = old_action_plan.get("routines", [])
        logger.debug(f"Total routines in old_plan: {len(old_routines)}")
        
        # Extract old routine IDs
        old_routine_ids = set()
        for routine in old_routines:
            rid = routine.get('routineUniqueId') or routine.get('routineId')
            if rid is None:
                logger.warning(f"Old routine missing both IDs: {routine}")
                continue
            logger.debug(f"Old routine id={rid}, name={routine.get('displayName','<no name>')}")
            old_routine_ids.add(rid)
        
        # Find matching routines in new data
        matching_routines = []
        pillar_stats_list = new_data.get('pillarCompletionStats', [])
        
        for pillar_idx, pillar in enumerate(pillar_stats_list):
            routines_list = pillar.get('routineCompletionStats', [])
            
            for routine_idx, routine in enumerate(routines_list):
                rid = routine.get('routineUniqueId') or routine.get('routineId')
                if rid is None:
                    logger.warning(f"New payload routine missing both IDs: {routine}")
                    continue
                    
                if rid in old_routine_ids:
                    logger.info(f"✅ Match found for id={rid} name={routine.get('displayName')}")
                    matching_routines.append({
                        "id": rid,
                        "name": routine.get('displayName'),
                        "statistics": routine.get('completionStatistics', [])
                    })
        
        return matching_routines
    
    @staticmethod
    def recalculate_action_plan(payload: Dict[str, Any], host: str) -> Dict[str, Any]:
        """
        Re-calculate an action plan by fetching the old plan from Strapi,
        finding matching routines, and returning their enriched list.
        """
        logger.info("=== RECALC_ACTION_PLAN START ===")
        
        unique_id = payload.get("actionPlanUniqueId")
        account_id = payload.get("accountId")
        
        if not unique_id:
            logger.error("Missing actionPlanUniqueId")
            return {"error": "missing-action-plan-id"}
        
        if account_id is None:
            logger.error("Missing accountId")
            return {"error": "missing-account-id"}
        
        try:
            old_plan = strapi_get_old_action_plan(unique_id, host)
        except Exception as e:
            logger.exception("Exception fetching old_plan")
            return {"error": "strapi-fetch-failed"}
        
        if not old_plan:
            logger.error(f"Strapi returned no plan for {unique_id}")
            return {"error": "not-found"}
        
        matching = ActionPlanService.print_matching_routine_details(
            new_data=payload,
            old_action_plan=old_plan
        )
        
        logger.info("=== RECALC_ACTION_PLAN END ===")
        return {
            "actionPlanUniqueId": unique_id,
            "matches": matching
        }
    
    @staticmethod
    def renew_action_plan(payload: Dict[str, Any], host: str) -> Dict[str, Any]:
        """
        Renew an action plan by cloning the old one and applying schedule changes.
        """
        unique_id = payload.get("actionPlanUniqueId")
        account_id = payload.get("accountId")
        
        logger.info(f"Renew action plan called with {unique_id}, {account_id}")
        
        if not unique_id or account_id is None:
            return {"error": "missing-action-plan-id" if not unique_id else "missing-account-id"}
        
        try:
            old_plan = strapi_get_old_action_plan(unique_id, host)
        except Exception as e:
            logger.error(f"Error fetching old plan: {e}")
            return {"error": "strapi-fetch-failed"}
        
        data_list = old_plan.get("data", [])
        if not data_list:
            return {"error": "not-found"}
        
        attrs = data_list[0].get("attributes", {})
        prev_id = attrs.get("actionPlanUniqueId")
        new_id = str(uuid.uuid4())
        
        logger.info(f"Cloning plan {prev_id} → {new_id}")
        
        # Process schedule changes from changeLog
        latest_changes = ActionPlanService._process_schedule_changes(payload.get("changeLog", []))
        
        # Apply changes to routines
        routines = attrs.get("routines", [])
        for routine in routines:
            rid = routine.get("routineUniqueId")
            if rid in latest_changes:
                routine["scheduleDays"] = latest_changes[rid]["scheduleDays"]
                logger.info(f"Applied new schedule to routine {rid}")
        
        # Build final action plan
        final_action_plan = {
            "data": {
                "actionPlanUniqueId": new_id,
                "previousActionPlanUniqueId": prev_id,
                "accountId": attrs.get("accountId"),
                "periodInDays": attrs.get("periodInDays"),
                "gender": attrs.get("gender", "").upper(),
                "totalDailyTimeInMins": attrs.get("totalDailyTimeInMins"),
                "routines": routines
            }
        }
        
        # Determine environment
        app_env = "development" if "dev" in host else "production"
        
        # Post to Strapi
        strapi_post_action_plan(final_action_plan, account_id, app_env)
        
        return final_action_plan
    
    @staticmethod
    def _process_schedule_changes(change_log: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
        """Process schedule changes from the change log"""
        latest_changes = {}
        
        for event in change_log:
            if (event.get("eventEnum") == "ROUTINE_SCHEDULE_CHANGE" and
                event.get("changeTarget") == "ROUTINE" and
                event.get("eventDetails", {}).get("scheduleCategory") == "WEEKLY_ROUTINE"):
                
                rid = int(event.get("targetId", 0))
                event_date = event.get("eventDate")
                
                for change in event.get("changes", []):
                    if change.get("changedProperty") == "SCHEDULE_DAYS":
                        raw = change.get("newValue", "[]")
                        try:
                            days = json.loads(raw)
                        except:
                            days = [int(c) for c in str(raw) if c.isdigit()]
                        
                        # Only update if this is the latest change
                        prev = latest_changes.get(rid)
                        if not prev or event_date > prev["eventDate"]:
                            latest_changes[rid] = {
                                "scheduleDays": days,
                                "eventDate": event_date
                            }
        
        return latest_changes