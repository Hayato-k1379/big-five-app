# Cleanup Targets

## Frontend
- Remove the unused `loading` refs in `frontend/src/views/SurveyView.vue` and `frontend/src/views/ResultView.vue`. Both views now rely solely on `ready`, so the extra state setters can be deleted without behavioural impact.

## Backend
- Prune legacy Django templates in `backend/survey/templates/survey/` (`survey.html`, `result.html`, `empty.html`). They are no longer rendered because every entry point redirects to the SPA.
- Drop the unused `SurveyForm` in `backend/survey/forms.py` and any code paths that referenced it historically.
- Revisit `spa_entry` in `backend/survey/views.py`: it renders `survey/spa_unbuilt.html`, which is missing. Decide whether to remove this view/route or replace it with a proper static asset response.

## Next Steps
1. Verify no deployment scripts rely on the legacy Django templates or form classes before deleting them.
2. Remove the identified frontend `loading` refs and confirm the SPA still loads normally.
3. Update the backend URLs/views to eliminate dead routes (`spa_entry`) and clean up related assets.
