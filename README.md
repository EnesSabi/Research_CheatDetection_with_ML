# Roadmap: Smurf Detection in League of Legends via Machine Learning

This notebook guides the step-by-step implementation of a machine learning pipeline for detecting smurf behavior in League of Legends. The project follows a prototyping approach based on weakly supervised learning, inspired by anomaly detection and ensemble modeling strategies.

---

## STEP 1: Setup & Preparation

- [x] Install required libraries:
1. RiotWatcher: a thin wrapper on top of the Riot Games API for League of Legends. [Doc-Link](https://riot-watcher.readthedocs.io/en/latest/)
2. Pandas: powerful Python data analysis toolkit [Doc-Link](https://pandas.pydata.org/docs/)
3. NumPy: the fundamental package for scientific computing with Python [Doc-Link](https://numpy.org/doc)
4. MatPlotLib: a comprehensive library for creating static, animated, and interactive visualizations in Python. [Doc-Link](https://matplotlib.org/)
5. Scikit-Learn: a Python module for machine learning built on top of SciPy [Doc-Link](https://scikit-learn.org/)
6. Python-DotEnv: reads key-value pairs from a .env file and can set them as environment variables [Doc-Link](https://pypi.org/project/python-dotenv/)



### Install dependecies
Make sure you have Python 3.12 and pip installed. Then run:

```bash
  pip install -r requirements.txt
```

### for updating pip

```bash
  python.exe -m pip install --upgrade pip
```

- [x] Register and get your Riot API Key at:  
  https://developer.riotgames.com/

- [x] Store your API key securely (in .env-File; excluded in GitRepo, but .env.example-File shows how it could look like)
### .env file

```bash
  RIOT_API_KEY=your_api_key_here
  REGION=europe
  PLATFORM=euw1
```

---

## STEP 2: Data Collection

- [ ] Use the Riot API to:

  - [x] Scrape OP.GG to extract active summoner names:
    - OP.GG provides useful public leaderboards but is rendered dynamically (JavaScript).
    - HTML blocks from OP.GG can be copied and parsed **offline** using BeautifulSoup (`bs4`) in the script `OP_GG_name_scraper.py`.
### OP.GG Name Scraper Example

```python
from bs4 import BeautifulSoup
import glob
import os

# Path to offline-saved HTML files
path = os.path.join(os.path.dirname(__file__), "NameScrapeTxt")
files = sorted(glob.glob(os.path.join(path, "*.txt")))

players = []

for file in files:
    with open(file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    for row in soup.select("tr"):
        name = row.select_one("span.whitespace-pre-wrap.text-gray-900")
        tag = row.select_one("span.text-gray-500.truncate")
        if name and tag:
            players.append(f"{name.text.strip()}{tag.text.strip()}")

# Remove duplicates and save results
players = list(set(players))
print(players)
print(f"{len(players)} Spieler gefunden")

with open("alle_spieler.txt", "w", encoding="utf-8") as f:
    for p in players:
        f.write(p + "\n")
```
  - [x] Download match data via Riot API:
    - Extracted summoner names are passed to `main_only_all_matches.py`.
    - This script uses `lol_watcher` and `riot_watcher` to retrieve the **most recent match** for each player.
    - Since each match contains 10 players, this approach helps **expand the dataset naturally**.
    - The resulting data is saved as a large `.json` file for further processing.
### API Fetch Example

```python
from riotwatcher import LolWatcher, RiotWatcher
from dotenv import load_dotenv
import os, time

# Load credentials
load_dotenv()
api_key = os.getenv("RIOT_API_KEY")
platform = os.getenv("PLATFORM")
region = os.getenv("REGION")

lol_watcher = LolWatcher(api_key)
riot_watcher = RiotWatcher(api_key)

def riot_api_request(func, *args, max_retries=3, sleep=2, **kwargs):
    for attempt in range(1, max_retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"[Retry {attempt}] {e}")
            if attempt == max_retries:
                raise
            time.sleep(sleep)

# Example: Fetch match IDs
account = riot_api_request(
    riot_watcher.account.by_riot_id,
    platform, "SummonerName", "TAG"
)
match_ids = riot_api_request(
    lol_watcher.match.matchlist_by_puuid,
    platform, account["puuid"], count=5
)
print(match_ids)
```

  - [x] Runtime & Infrastructure:
    - Due to Riot API rate limits, the full match collection can be executed on an **AWS EC2 instance**.
    - This enables uninterrupted batch processing over longer time periods.

- [ ] Use the Riot Live-Client API to (for version 2.0):
  - Track real-time in-game data during active matches
  - Extract live match snapshots (every 5 seconds)
  - Automatically generate match-specific JSON logs for each user
  - Build and distribute a `.exe` GUI tool that runs on any Windows system
    - Create an `.exe` file using the command *pyinstaller --noconsole --onefile program_live.py* in the virutal environment terminal
      - This ensures that no console is visible and that all imports are included in the `.exe` file
    - Users can start/stop live extraction via graphical interface
    - Snapshots are stored locally and optionally uploaded to a central server for aggregation


---

## STEP 3: Feature Engineering

This step transforms raw gameplay data into structured machine learning input. It includes several preprocessing steps and the design of domain-specific features to detect smurf behavior effectively.

### 1. Data Cleaning and Preparation

- **Missing Values**: Missing numerical values are imputed using the mean or median; categorical columns are imputed using the most frequent value.
- **Column Filtering**: Redundant columns and constant features are dropped to reduce noise and overfitting.
- **Encoding**: Categorical features (such as `role`) are one-hot encoded, depending on the model context. Whereas ordinal features are ordinal-encoded
- **Outlier Filtering**: Some filters (e.g., minimum game count or suspicious match duration) are used to remove invalid matches or rare outliers.
- **Type Conversion**: Several string-based numbers are converted into `float` or `int` for computation.

### 2. Core Feature Extraction

The following features are derived or selected from the match data:

- `kills`, `deaths`, `assists`, `goldEarned`, `damageDealt`
- `kda`, `damageShare`, `killShare`, `visionPerMinute`
- `summonerLevel`, `skillshotsHit`, `dodgeSkillShotsSmallWindow`
- `perfectGame`, `firstBloodKill`, `objectiveSteals`
- `maxCsAdvantageOnLaneOpponent`, `maxLevelLead`, `timeDead`
- `turretPlatesTaken`, `wardsTakedownBefore20M`, `hotStreak`

These features are designed to capture mechanical skill, team contribution, and player dominance in matches.

### 3. Heuristic Features (for Weak Labels)

To simulate smurf behavior (since no ground truth exists), we engineered a custom score (`smurf_score`) and binary label (`smurf_flag`) using domain knowledge and rules such as:

- High APM or `kills` in early game
- Low summoner level but high winrate or performance
- High CS lead, vision score, or perfect game count
- Low number of deaths or ragequits (filtered via `earlySurrender` and `AFK`-proxy)
- First-to-level-6 events and fast item completion

Features were combined into a weighted score to assign weakly supervised labels:
- `0` = Normal player
- `1` = Smurf (high-performing anomaly)
- `2` = Suspicious/Boosted (potential low-quality anomaly)

These labels are used as training or evaluation targets for classification and anomaly detection models.

### 4. Normalization and Dimensionality Reduction

- All features are standardized using `StandardScaler`.
- Dimensionality reduction via `PCA` is applied prior to training anomaly detection models, where the number of components is tunable (e.g., 0.95 or 0.85 variance explained).

---

## STEP 4: Model Training

The training pipeline consists of two parallel approaches: **unsupervised anomaly detection** and **supervised classification**, both evaluated using the same weakly supervised label (`smurf_flag`).

### 1. Unsupervised Ensemble (Anomaly Detection)

To detect outliers that behave significantly different from the norm (e.g., smurfs), four anomaly detection models are trained:

- `IsolationForest`
- `OneClassSVM`
- `LocalOutlierFactor` (with `novelty=True`)
- `Autoencoder` (trained with MSE reconstruction loss)

Each model predicts anomalies independently. A **majority vote (Bagging Ensemble)** was used to aggregate predictions:

- Players marked as anomalies by at least **2 out of 4 models** were labeled as predicted smurfs.
- This approach increases robustness across varying model sensitivities.

### 2. Supervised Classification

Two ensemble supervised models were trained on features with the weak label `smurf_flag`:

- `RandomForestClassifier`
- `XGBoostClassifier` with `scale_pos_weight` for handling imbalance

Models were trained on standardized features, reduced via PCA, and evaluated on held-out test sets.
---

## STEP 5: Evaluation

All models — both supervised and unsupervised — are evaluated using standard classification metrics. Since ground truth labels are derived heuristically (`smurf_flag`), this step assesses how well the models can replicate or generalize the heuristic logic.

### Evaluation Metrics

- **Classification Report**:  
  Precision, Recall, F1-Score for both classes (`normal`, `smurf`)  
  → Key metric to balance false positives vs. false negatives

- **Confusion Matrix**:  
  Visual breakdown of true/false positives and negatives  
  → Useful to identify dominant error types

- **ROC-AUC Score**:  
  Area under the receiver operating characteristic curve  
  → Measures the model's ability to distinguish between classes

- **PR-AUC Score**:  
  Area under the precision–recall curve  
  → Measures how well the model identifies the positive class across different decision thresholds, especially under strong class imbalance

- **Voting Threshold Sensitivity**:  
  For unsupervised models, majority vote thresholds (e.g., ≥2 of 4) are varied  
  → Higher thresholds reduce false positives but may lower recall

- **PCA Robustness Sweep**:  
  Evaluation was repeated for different PCA compression levels  
  → Shows how much variance is needed to retain classification quality
- **General Model Hyperparameter Tuning**  
  Key hyperparameters (e.g., number of estimators, `nu`, `contamination`, learning rate) were varied and tested  
  → Ensures models are neither overfitting nor underfitting the weak supervision signal

### Remarks

- Evaluation was always done on a held-out test set using stratified splits.
- High Recall with low Precision in unsupervised models indicates strong anomaly sensitivity, but also more false alarms. Achieved a good PR-AUC score (≈0.25)
- Supervised models like XGBoost achieved high ROC-AUC (≥0.90) and PR-AUC (≈0.80) even with dimensionality reduction, indicating strong separability.

> All evaluations were performed against the weak label `smurf_flag`, which approximates true smurf behavior through engineered heuristics.  
> This label is not manually verified and may contain noise or incorrect assignments.  
> Therefore, the models are not expected to achieve perfect alignment, but rather to generalize the underlying behavioral patterns.   
> PR-AUC values should be interpreted relative to the class distribution.
> In this dataset, the positive class represents approximately 2.5 %, which corresponds to the random baseline for PR-AUC.


---

## STEP 6: Privacy & Ethics

- [ ] Game Rules und Terms of Use from Riot Games
- [ ] Show how FL preserves user data privacy
- [ ] Mention compliance topics (e.g., GDPR) and ethical detection strategies
- [ ] DSGVO compliance

---

# Routing Values

| Platform | Host                   | Region                  |
|----------|------------------------|-------------------------|
| BR1      | br1.api.riotgames.com  | Brazil                  |
| EUN1     | eun1.api.riotgames.com | Europe Nordic & East    |
| EUW1     | euw1.api.riotgames.com | Europe West             |
| JP1      | jp1.api.riotgames.com  | Japan                   | 
| KR       | kr.api.riotgames.com   | Korea                   |
| LA1      | la1.api.riotgames.com  | Latin America North     |
| LA2      | la2.api.riotgames.com  | Latin America South     |
| NA1      | na1.api.riotgames.com  | North America           |
| OC1      | oc1.api.riotgames.com  | Oceania                 |
| TR1      | tr1.api.riotgames.com  | Turkiye                 |
| RU       | ru.api.riotgames.com   | Russia                  |
| PH2      | ph2.api.riotgames.com  | Philippines             |
| SG2      | sg2.api.riotgames.com  | Singapore               |
| TH2      | th2.api.riotgames.com  | Thailand                |
| TW2      | tw2.api.riotgames.com  | Taiwan, HongKong, Macao |
| VN2      | vn2.api.riotgames.com  | Vietnam                 |

---

# Developer API Policy

## Abide by following
- Products cannot violate any laws.
- Do not create or develop games utilizing Riot’s Intellectual Property (IP).
- No cryptocurrencies or no blockchain.
- No apps serving as a “data broker” between our API and another third-party company.
- Products cannot closely resemble Riot’s games or products in style or function.
- Only the following Riot IP assets may be used in the development and marketing of your product:
  - Press kit
  - Example: Using Riot logos and trademarks from the Press Kit must be limited to cases where such use is unavoidable in order to serve the core value of the product.
  - Game-Specific static data
- You must post the following legal boilerplate to your product in a location that is readily visible to players:
  - Research_CheatDetection_with_ML is not endorsed by Riot Games and does not reflect the views or opinions of Riot Games or anyone officially involved in producing or managing Riot Games properties. Riot Games and all associated properties are trademarks or registered trademarks of Riot Games, Inc

## Monetization
**To monetize your product, you must abide by the following:**

- Your product cannot feature betting or gambling functionality.
- Your product must be registered on the Developer Portal and your product status is either Approved or Acknowledged.
- You must have a free tier of access for players, which may include advertising.
- Your content must be transformative if you are charging players for it.
  - What is transformative?
    - Was value added to the original by creating new information, new aesthetics, new insights, and understandings? If so, then it was transformative.
  - **Acceptable ways to charge players are:**
    - Subscriptions, donations, or crowdfunding.
    - Entry fees for tournaments.
    - Currencies that cannot be exchanged back into fiat.
  - Your monetization cannot gouge players or be unfair, as decided by Riot. 
If you are unsure if your monetization platform is acceptable, contact us through the Developer Portal.

## Security
You must adhere to the following security policies:

- Do not share your Riot Games account information with anyone.
- Do not use a Production API key to run multiple projects. You may only have one product per key.
- Use SSL/HTTPS when accessing the APIs so your API key is kept safe.
- Your API key may not be included in your code, especially if you plan on distributing a binary.
  - This key should only be shared with your teammates. If you need to share an API key for your product with teammates, make sure your product is owned by a group in the Developer portal. Add additional accounts to that account as needed.

## Game Integrity
- Products must not use or incorporate information not present in the game client that would give players a competitive edge (e.g., automatically or manually allowing tracking enemy ultimate cooldowns), especially when such data is not already accessible through regular gameplay.
- Products cannot alter the goal of the game (i.e. Destroy the Nexus).
- Products cannot create an unfair advantage for players, like a cheating program or giving some players an advantage that others would not otherwise have.
- Products should increase, and not decrease the diversity of game decisions (builds, compositions, characters, decks).
- Products should not remove game decisions, but may highlight decisions that are important and give multiple choices to help players make good decisions.
- Products cannot create alternatives for official skill ranking systems such as the ranked ladder. Prohibited alternatives include MMR or ELO calculators.
- Products cannot identify or analyze players who are deliberately hidden by the game.






