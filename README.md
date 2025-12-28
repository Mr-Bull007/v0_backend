# Khel Club Tournament Management System - Walkover Feature Implementation

## Overview

This document describes the implementation of the **Walkover** match outcome feature for the Khel Club tournament management system. The walkover feature allows referees to record matches where one team is unable to compete, ensuring proper tournament progression and accurate record-keeping.

## Demo Video

📹 **Screen Recording**: [View Walkover Feature Demo](https://drive.google.com/file/d/1ph6_h-mEjidTMBXtyZVyD1Wp5jnR_Rda/view?usp=sharing)

The demo video shows the walkover feature working end-to-end, including:

- Navigating to the referee portal
- Marking a match as walkover
- Viewing walkover badges in all UI components
- Walkover details display in match overlays

---

## How the Current Scoring Mechanism Works

### Normal Match Scoring

The scoring system operates as follows:

1. **Score Entry**: Referees enter scores in the format `{teamA_score}-{teamB_score}` (e.g., "21-15")
2. **Score Storage**:
   - Each match has two `Score` records (one per team) stored in the `score` table
   - Scores are linked to `match_id`, `team_id`, and `tournament_id`
3. **Winner Determination**:
   - When a match is finalized (`final=true`), the system compares `team1_score` and `team2_score`
   - The team with the higher score is set as `winner_team_id`
   - If scores are equal, `winner_team_id` is set to `NULL` (draw)
4. **Match Finalization**:
   - Setting `final=true` marks the match as complete (`is_final=True`)
   - The match status is updated accordingly
   - For knockout/bracket matches, the winner automatically advances to the next round via the `update_successor_match()` function
5. **Points Calculation**:
   - Points are calculated by summing all `Score.score` values for a team across all matches
   - Points can be queried at tournament, pool, or round level
   - Points are used for pool standings and tournament rankings

### Match States

- **Pending**: Match has not started
- **In Progress**: Match is currently being played
- **Completed**: Match has been finalized with a winner

### Tournament Structure

- **Pool Play**: Teams compete in pools, with points accumulated across matches
- **Knockout/Bracket**: Winners advance to subsequent rounds based on predecessor matches
- **Successor Match Updates**: When a match is finalized, the system automatically updates the next round's match with the winning team

---

## Changes Made and Why

### 1. Database Schema Changes

**Added three new columns to the `match` table:**

- `result_type` (VARCHAR(20), nullable): Indicates the type of match result

  - Values: `'normal'` (default), `'walkover'`
  - **Why**: Provides a scalable way to distinguish between different match outcomes without hardcoding logic

- `walkover_reason` (VARCHAR(30), nullable): Stores the reason for a walkover

  - Examples: "team_1_absent", "team_2_absent", "injury", etc.
  - **Why**: Allows tracking why a walkover occurred for administrative and reporting purposes

- `winner_source` (VARCHAR(20), nullable): Indicates how the winner was determined
  - Values: `'score'` (from normal scoring), `'walkover'`, `'admin'` (future use)
  - **Why**: Provides audit trail and allows for future match outcome types (e.g., forfeit, bye, admin decision)

**Files Modified:**

- `models.py`: Added the three new columns to the `Match` class
- `dump-test-202512221924.sql`: Updated `CREATE TABLE match` statement and `INSERT` statements to include the new columns

### 2. Backend API Changes

#### `routes/score/score_core.py`

**Modified `update_score()` endpoint:**

- Added `result_type` parameter validation (accepts `'normal'` or `'walkover'`)
- Implemented walkover handling logic:
  - Requires `winner_team_id` and optional `walkover_reason`
  - Sets `match.is_final = True`
  - Sets `match.result_type = 'walkover'`
  - Sets `match.winner_source = 'walkover'`
  - Does NOT create `Score` records (walkovers have no scores)
  - Still updates successor matches for bracket progression
- For normal matches, sets `match.winner_source = 'score'` when finalized
- Returns `result_type`, `walkover_reason`, and `winner_source` in API responses

**Modified `get_match_score()` endpoint:**

- Added `result_type`, `walkover_reason`, and `winner_source` to the response JSON
- Allows frontend to display walkover information

#### `routes/match/match_fixtures.py`

**Modified `get_match_fixtures()` endpoint:**

- Added `result_type`, `walkover_reason`, and `winner_source` to the fixture JSON response
- Ensures all match display components receive walkover data

### 3. Frontend Changes

#### Components Updated for Walkover Display

1. **`components/matchTable/MatchTable.js`**

   - Added "WALKOVER" badge in the Result column for walkover matches
   - Fixed CSV export `removeChild` error

2. **`components/fixtures/Fixtures.js`**

   - Added "WALKOVER" badge on match cards for walkover matches

3. **`components/matchOverlay/MatchOverlay.js`**

   - Displays walkover details (badge, winner, reason) when viewing a walkover match
   - Hides score inputs for walkover matches

4. **`components/refereeMatchTable/RefereeMatchTable.js`**

   - Added "WALKOVER" badge in the Result column

5. **`screen/referee/match/Match.js`**

   - Added "Mark as Walkover" button
   - Implemented modal for selecting winning team and entering walkover reason
   - Disables score inputs when match is already a walkover
   - Displays walkover details (winner, reason) when viewing a walkover match

6. **`screen/Landing/Landing.js`**
   - Added "Go to Referee Portal" button for easier navigation during testing

#### Styling Updates

- Added CSS styles for `.walkoverBadge` in multiple SCSS files
- Consistent styling across all components (orange/amber background, dark text)

### 4. Configuration Changes

#### `config.py`

- Switched from `mysqlclient` to `pymysql` driver (Windows compatibility)
- Added URL encoding for database password to handle special characters
- Updated SQLAlchemy connection string to use `mysql+pymysql://`

#### `requirements.txt`

- Replaced `mysqlclient` with `pymysql` to avoid Windows compilation issues

---

## Schema and Migration Changes

### Migration Files Created

1. **`migrations/bul/2025_01_add_match_result_columns.py`**

   - Python script that checks for column existence and adds them if missing
   - Idempotent migration (safe to run multiple times)

2. **`migrations/bul/2025_01_add_match_result_columns.sql`**
   - Raw SQL migration script
   - Adds the three new columns using `ALTER TABLE` statements

### SQL Dump Updates

**`dump-test-202512221924.sql`:**

- Updated `CREATE TABLE match` to include:
  ```sql
  `result_type` varchar(20) DEFAULT NULL,
  `walkover_reason` varchar(30) DEFAULT NULL,
  `winner_source` varchar(20) DEFAULT NULL
  ```
- Updated all `INSERT INTO match` statements to include three `NULL` values for existing matches
- Commented out `GTID_PURGED` line to avoid replication conflicts in local development

### Migration Approach

Since this is an assignment project with a provided SQL dump, the migration was handled by:

1. Updating the SQL dump file directly (for new database setups)
2. Creating migration scripts for existing databases (Python and SQL versions provided)

**Note**: Migration files in `migrations/bul/` are provided for reference but were not executed in this setup, as the dump file was updated directly.

---

## Assumptions Made

1. **Walkover Matches Have No Scores**: Walkover matches do not create `Score` records. Only the `winner_team_id` is set.

2. **Walkover Still Advances Winners**: Even though there are no scores, walkover matches still update successor matches in knockout brackets, allowing tournament progression.

3. **Walkover is Final**: Once a match is marked as walkover, it is immediately finalized (`is_final=True`). There is no "pending walkover" state.

4. **Winner Must Be One of the Two Teams**: The `winner_team_id` for a walkover must be either `team1_id` or `team2_id`. The system validates this.

5. **Walkover Reason is Optional**: The `walkover_reason` field is optional but recommended for record-keeping.

6. **No Points for Walkovers**: Since walkover matches don't have scores, they don't contribute to team points calculations. This is intentional - walkovers are administrative decisions, not competitive results.

7. **Scalability**: The `result_type` and `winner_source` fields are designed to be extensible. Future match outcomes (e.g., "forfeit", "bye", "admin_decision") can be added by:

   - Adding new values to the validation list in `update_score()`
   - Adding corresponding UI elements in the frontend
   - No schema changes needed (unless new fields are required)

8. **Backward Compatibility**: Existing matches without `result_type` are treated as `'normal'` matches. The system defaults to `'normal'` when `result_type` is `NULL`.

9. **Database Setup**: The project uses a provided SQL dump for initial setup. Migration scripts are provided for reference but may not be needed if starting fresh.

10. **Frontend-Backend Communication**: The frontend sends `result_type`, `winner_team_id`, and `walkover_reason` in the request body when marking a walkover. The backend validates and processes accordingly.

---

## What Would Be Improved If Given More Time

### 1. **Enhanced Walkover Reasons**

- **Current**: Free-text or simple dropdown
- **Improvement**: Structured reason codes with categories (e.g., "no_show", "injury", "disqualification", "withdrawal") with optional notes
- **Benefit**: Better analytics and reporting on why walkovers occur

### 2. **Walkover Notifications**

- **Current**: Walkover is recorded silently
- **Improvement**: Email/SMS notifications to affected teams and tournament organizers
- **Benefit**: Better communication and transparency

### 3. **Walkover History and Audit Trail**

- **Current**: Only current walkover reason is stored
- **Improvement**: Log all walkover changes with timestamps, user who made the change, and reason changes
- **Benefit**: Full audit trail for administrative decisions

### 4. **Points System for Walkovers**

- **Current**: Walkovers don't contribute to points
- **Improvement**: Configurable points for walkover wins/losses (e.g., +1 point for walkover win, 0 for loss)
- **Benefit**: Fairer point distribution in some tournament formats

### 5. **Walkover Prevention**

- **Current**: Walkovers are recorded after the fact
- **Improvement**: Early warning system for teams at risk of no-show (e.g., check-in reminders, automated follow-ups)
- **Benefit**: Reduce walkover occurrences

### 6. **Referee Permissions**

- **Current**: Any referee can mark a walkover
- **Improvement**: Role-based permissions (e.g., only head referees or admins can mark walkovers)
- **Benefit**: Prevent abuse and ensure proper authorization

### 7. **Walkover Reversal**

- **Current**: Once marked as walkover, it's final
- **Improvement**: Allow admins to reverse walkovers (with proper audit trail) if a team shows up late or if there was an error
- **Benefit**: Handle edge cases and errors gracefully

### 8. **Statistics and Reporting**

- **Current**: Basic walkover display
- **Improvement**: Dashboard showing walkover rates, most common reasons, teams with frequent walkovers
- **Benefit**: Identify patterns and improve tournament management

### 9. **Multi-language Support**

- **Current**: UI text is in English
- **Improvement**: Internationalization (i18n) for walkover-related UI elements
- **Benefit**: Support for diverse user base

### 10. **Automated Walkover Detection**

- **Current**: Manual walkover marking
- **Improvement**: Auto-mark walkover if a team doesn't check in by match time (with configurable grace period)
- **Benefit**: Reduce manual work and ensure timely tournament progression

### 11. **Walkover in Pool Standings**

- **Current**: Walkovers don't affect pool calculations
- **Improvement**: Display walkover matches in pool standings with clear indicators, and optionally count them in win/loss records
- **Benefit**: More complete tournament view

### 12. **API Documentation**

- **Current**: Code comments and this README
- **Improvement**: OpenAPI/Swagger documentation for the walkover endpoints
- **Benefit**: Easier integration and testing

### 13. **Unit and Integration Tests**

- **Current**: Manual testing
- **Improvement**: Comprehensive test suite covering:
  - Walkover creation and validation
  - Successor match updates for walkovers
  - Points calculation exclusion for walkovers
  - Edge cases (invalid winner_team_id, missing fields, etc.)
- **Benefit**: Ensure reliability and catch regressions

### 14. **Frontend Form Validation**

- **Current**: Basic validation
- **Improvement**: Enhanced client-side validation with clear error messages, required field indicators, and real-time feedback
- **Benefit**: Better user experience and fewer API errors

### 15. **Mobile Responsiveness**

- **Current**: Basic responsive design
- **Improvement**: Optimized mobile UI for walkover marking (larger buttons, simplified modal, touch-friendly)
- **Benefit**: Referees can mark walkovers on mobile devices easily

---

## Technical Implementation Details

### API Endpoints

#### `POST /update-score`

**Request Body (Walkover):**

```json
{
  "match_id": 123,
  "tournament_id": 1,
  "result_type": "walkover",
  "winner_team_id": "T001",
  "walkover_reason": "team_2_absent"
}
```

**Response:**

```json
{
  "message": "Walkover recorded",
  "match_id": 123,
  "winner_team_id": "T001",
  "result_type": "walkover",
  "walkover_reason": "team_2_absent"
}
```

#### `GET /score/match?match_id=123&tournament_id=1`

**Response (includes walkover fields):**

```json
{
  "match_id": 123,
  "tournament_id": 1,
  "team1": { ... },
  "team2": { ... },
  "status": "completed",
  "is_final": true,
  "winner_team_id": "T001",
  "result_type": "walkover",
  "walkover_reason": "team_2_absent",
  "winner_source": "walkover"
}
```

### Database Schema

```sql
ALTER TABLE `match`
ADD COLUMN `result_type` VARCHAR(20) NULL,
ADD COLUMN `walkover_reason` VARCHAR(30) NULL,
ADD COLUMN `winner_source` VARCHAR(20) NULL;
```

### Frontend State Management

- Walkover state is managed via React `useState` hooks
- Modal state controls walkover form visibility
- Form data is validated before submission
- WebSocket updates (if configured) will reflect walkover changes in real-time

---

## Testing Checklist

- [x] Backend API accepts walkover requests
- [x] Walkover matches are marked as final
- [x] Walkover matches don't create score records
- [x] Walkover matches update successor matches correctly
- [x] Frontend displays walkover badges in all relevant components
- [x] Walkover modal allows selecting winner and entering reason
- [x] Score inputs are disabled for walkover matches
- [x] Walkover details are displayed in match overlay
- [x] Database schema includes new columns
- [x] SQL dump includes new columns
- [x] Backward compatibility maintained (NULL result_type treated as 'normal')

---

## Conclusion

The walkover feature has been successfully implemented with a scalable design that allows for future match outcome types. The implementation maintains backward compatibility, follows existing code patterns, and provides a clear user experience for referees to record walkover matches. The system is ready for production use with the current feature set, and the architecture supports easy extension for additional match outcomes in the future.
