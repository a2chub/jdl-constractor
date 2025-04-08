# backend/app/services/data_integrity_service.py
import logging
from collections import defaultdict
from typing import List, Dict, Any

from google.cloud import firestore

# Assuming firebase client is initialized similarly elsewhere
# If not, initialize it here or pass it in
try:
    from app.core.firebase import db
except ImportError:
    # Fallback or error handling if firebase core setup is different
    logging.error("Failed to import Firestore client from app.core.firebase")
    # You might need to initialize db differently based on script execution context
    # For simplicity, assume db is available or handle initialization in the script
    # In a real scenario, ensure db is properly initialized before using the service.
    db = None # Or raise an error

logger = logging.getLogger(__name__)

class DataIntegrityService:
    """
    Provides methods to check data integrity within the Firestore database.
    """

    def __init__(self, firestore_db: firestore.Client = db):
        if firestore_db is None:
            # Attempt to initialize if not provided and import failed? Risky.
            # Better to ensure it's passed correctly or initialized globally.
            try:
                 # Try initializing again, might work depending on context
                 from app.core.firebase import db as initialized_db
                 if initialized_db is None:
                      raise ValueError("Firestore client (db) could not be initialized.")
                 self.db = initialized_db
                 logger.info("Firestore client initialized within DataIntegrityService.")
            except Exception as e:
                 logger.error(f"Failed to initialize Firestore client: {e}")
                 raise ValueError("Firestore client (db) is not available.") from e
        else:
             self.db = firestore_db

        self.players_ref = self.db.collection('players')
        self.teams_ref = self.db.collection('teams')
        # Add other collections as needed (e.g., tournaments, class_changes)

    def check_duplicate_jdl_ids(self) -> List[Dict[str, Any]]:
        """
        Checks for duplicate JDL IDs in the players collection.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each containing
                                  'jdl_id' and 'document_ids' for duplicates.
        """
        logger.info("Checking for duplicate JDL IDs...")
        jdl_id_map = defaultdict(list)
        duplicates = []

        try:
            docs = self.players_ref.stream()
            count = 0
            for doc in docs:
                count += 1
                data = doc.to_dict()
                if data and 'jdl_id' in data:
                    jdl_id = data['jdl_id']
                    if jdl_id: # Ensure jdl_id is not empty
                        jdl_id_map[jdl_id].append(doc.id)
                elif data is None:
                     logger.warning(f"Document {doc.id} in players collection has no data (None).")
                elif 'jdl_id' not in data:
                     logger.warning(f"Document {doc.id} in players collection is missing 'jdl_id' field.")


            logger.info(f"Processed {count} player documents for duplicate JDL ID check.")

            for jdl_id, doc_ids in jdl_id_map.items():
                if len(doc_ids) > 1:
                    duplicates.append({"jdl_id": jdl_id, "document_ids": doc_ids})
                    logger.warning(f"Duplicate JDL ID found: {jdl_id} in documents {doc_ids}")

        except Exception as e:
            logger.exception(f"Error checking duplicate JDL IDs: {e}")
            # Optionally re-raise or return an error indicator

        logger.info(f"Duplicate JDL ID check complete. Found {len(duplicates)} JDL IDs with duplicates.")
        return duplicates

    def check_broken_team_references(self) -> List[Dict[str, Any]]:
        """
        Checks for players referencing non-existent teams.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each containing
                                  'player_doc_id', 'jdl_id', and 'broken_team_id'.
        """
        logger.info("Checking for broken team references in players...")
        broken_references = []
        existing_team_ids = set()

        try:
            # Get all existing team IDs first for efficient lookup
            team_docs = self.teams_ref.select([]).stream() # Only fetch IDs (more efficient)
            existing_team_ids = {doc.id for doc in team_docs}
            logger.info(f"Found {len(existing_team_ids)} existing team IDs.")

            if not existing_team_ids:
                 logger.warning("No teams found in the database. Cannot perform team reference check accurately.")
                 # Depending on requirements, might return early or proceed

            player_docs = self.players_ref.stream()
            player_count = 0
            for player_doc in player_docs:
                player_count += 1
                player_data = player_doc.to_dict()
                # Check if player_data exists and team_id is present and not None/empty
                if player_data and 'team_id' in player_data and player_data['team_id']:
                    team_id = player_data['team_id']
                    if team_id not in existing_team_ids:
                        broken_info = {
                            "player_doc_id": player_doc.id,
                            "jdl_id": player_data.get('jdl_id', 'N/A'), # Include JDL ID for easier identification
                            "broken_team_id": team_id
                        }
                        broken_references.append(broken_info)
                        logger.warning(f"Broken team reference found: Player {player_doc.id} (JDL: {broken_info['jdl_id']}) references non-existent team {team_id}")
                # Optional: Log players with missing or null team_id if that's considered an issue
                # elif player_data and ('team_id' not in player_data or not player_data['team_id']):
                #     logger.debug(f"Player {player_doc.id} has no team_id assigned.")

            logger.info(f"Processed {player_count} player documents for broken team references.")

        except Exception as e:
            logger.exception(f"Error checking broken team references: {e}")

        logger.info(f"Broken team reference check complete. Found {len(broken_references)} broken references.")
        return broken_references

    # --- Add more checks as needed ---
    # Example: Check class consistency (e.g., player.current_class vs class_history)
    # Example: Check tournament entry validity (e.g., entry references existing player/team/tournament)

    def run_all_checks(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Runs all defined integrity checks.

        Returns:
            Dict[str, List[Dict[str, Any]]]: A dictionary where keys are check names
                                             and values are the lists of inconsistencies.
        """
        logger.info("Running all data integrity checks...")
        results = {}
        try:
            results["duplicate_jdl_ids"] = self.check_duplicate_jdl_ids()
        except Exception as e:
            logger.error(f"Failed to run check_duplicate_jdl_ids: {e}")
            results["duplicate_jdl_ids"] = [{"error": str(e)}]

        try:
            results["broken_team_references"] = self.check_broken_team_references()
        except Exception as e:
            logger.error(f"Failed to run check_broken_team_references: {e}")
            results["broken_team_references"] = [{"error": str(e)}]

        # Add results from other checks here
        # try:
        #     results["other_check"] = self.run_other_check()
        # except Exception as e:
        #     logger.error(f"Failed to run run_other_check: {e}")
        #     results["other_check"] = [{"error": str(e)}]

        logger.info("All data integrity checks finished.")
        return results
