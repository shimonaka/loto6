# Loto 6 Predictor Upgrade Implementation Plan

## Goal Description
Upgrade the existing `loto6_predictor.html` system to automatically fetch the latest Loto 6 results from the web and incorporate historical data from 2000 to present. This will replace the hardcoded data with a dynamic updating mechanism driven by a Python script.

## User Review Required
> [!IMPORTANT]
> This upgrade introduces a Python dependency (`update_loto6.py`) and requires `requests` and `beautifulsoup4` libraries. The user will need to run this Python script to update the data.

## Proposed Changes

### Data Acquisition & Management
#### [NEW] [update_loto6.py](file:///c:/Users/shimo/Desktop/loto6/update_loto6.py)
- **Purpose**: Scrape latest and historical data, merge, and save to `loto6_data.js`.
- **Key Functions**:
    - `fetch_page(url)`: Generic fetcher.
    - `parse_table(html)`: Extracts numbers, dates, and bonus numbers.
    - `update_data()`: Main logic to orchestrate fetching (iterating years 2000-current).
    - Writes data to `loto6_data.js` as a JavaScript variable assignment.
- **Optimization**: Checks existing data and only fetches new years (incremental update).

#### [NEW] [loto6_data.js](file:///c:/Users/shimo/Desktop/loto6/loto6_data.js)
- **Purpose**: Storage for the dataset in a format directly loadable by the browser (avoiding CORS/file:// JSON restrictions).
- **Format**: `const LOTO6_DATA = [...];`

### Frontend Application
#### [MODIFY] [loto6_predictor.html](file:///c:/Users/shimo/Desktop/loto6/loto6_predictor.html)
- **Remove**: Hardcoded `historicalData` array.
- **Add**: `<script src="loto6_data.js"></script>` reference.
- **Update**: Initialization logic to use the external `LOTO6_DATA` variable.
- **UI**: Added a display for "Latest Data Date" (最新データ日) in the statistics summary.

### Launcher
#### [NEW] [start.bat](file:///c:/Users/shimo/Desktop/loto6/start.bat)
- Automated script to update data via Python and then launch the HTML file.

## Verification Plan

### Automated Tests
- Script-based verification of data fetching and parsing.

### Manual Verification
1.  **Install Dependencies**: `pip install requests beautifulsoup4`
2.  **Run Updater**: Execute `start.bat`.
    - Verify `loto6_data.js` is updated.
    - Verify browser opens with correct latest date shown.
