# Roadmap: Federated Learning Cheat Detection in League of Legends

This notebook will guide the step-by-step implementation of a federated learning system for detecting cheating behavior in *League of Legends*. The structure follows a prototype inspired by the FedFusion framework.

---

## STEP 1: Setup & Preparation

- [x] Install required libraries:
1. RiotWatcher: a thin wrapper on top of the Riot Games API for League of Legends. [Doc-Link](https://riot-watcher.readthedocs.io/en/latest/)
2. Pandas: powerful Python data analysis toolkit [Doc-Link](https://pandas.pydata.org/docs/)
3. NumPy: the fundamental package for scientific computing with Python [Doc-Link](https://numpy.org/doc)
4. MatPlotLib: a comprehensive library for creating static, animated, and interactive visualizations in Python. [Doc-Link](https://matplotlib.org/)
5. Scikit-Learn: a Python module for machine learning built on top of SciPy [Doc-Link](https://scikit-learn.org/)
6. Python-DotEnv: reads key-value pairs from a .env file and can set them as environment variables [Doc-Link](https://pypi.org/project/python-dotenv/)


### for updating pip

```bash
  python.exe -m pip install --upgrade pip
```
### install dependecies

```bash
  pip install riotwatcher pandas numpy matplotlib scikit-learn python-dotenv
```

- [x] Register and get your Riot API Key at:  
  https://developer.riotgames.com/

- [x] Store your API key securely (in .env-File; excluded in GitRepo)

---

## STEP 2: Data Collection

- [ ] Use the Riot API to:
  - Fetch a summoner profile by name
    - To fetch summoner data, we need the RiotID containing gameName and tagLine
    - best Website OP.gg to find the best players
  - Retrieve recent match IDs
  - Download match details (participants, stats, timeline)

*First Goal: Create a JSON dataset from 10 to 50 matches for a few players (mostly friends first)*

---

## STEP 3: Feature Engineering

- [ ] Extract features such as: (will be extended with new attributes)
  - `kills`, `deaths`, `assists`, `goldEarned`, `damageDealt`
  - APM (Actions per Minute), item timings, spell usage
- [ ] Build a structured pandas DataFrame
- [ ] Simulate labels (e.g., `0 = normal`, `1 = suspicious`)(optional: float between 0 and 1 for identification)

---

## STEP 4: Local Model Training (per Client)

- [ ] Simulate 2–3 different clients (e.g., regions EUW, JPN, KR, TR)
- [ ] Train one model per client (e.g., DL, RandomForest, MLP)
- [ ] Evaluate each model’s performance individually

---

## STEP 5: Adaptive Model Fusion

- [ ] Combine local models using weighted averaging:
  - Use a fusion parameter `alpha`
  - Optionally: adapt `alpha` based on performance

---

## STEP 6: Evaluation

- [ ] Compare local vs. global model:
  - Accuracy, Recall, Precision, F1-score

- [ ] Visualize:
  - Confusion matrix
  - Prediction distributions

---

## STEP 7: Visualization & Explainability

- [ ] Visualize clusters using **t-SNE**
- [ ] Explain model predictions using **SHAP**

---

## STEP 8: Privacy & Ethics

- [ ] Game Rules und Terms of Use from Riot Games
- [ ] Show how FL preserves user data privacy
- [ ] Mention compliance topics (e.g., GDPR) and ethical detection strategies
- [ ] DSGVO compliance

---

## STEP 9: Final Notebook and Paper Sections

Structure for presentation:

1. **Introduction & Goals**
2. **Data Collection (Riot API, Pandas)**
3. **Feature Extraction**
4. **Model Training per Client**
5. **Adaptive Model Fusion**
6. **Evaluation**
7. **Visualizations (t-SNE, SHAP)**
8. **Discussion & Limitations**

---

# Routing Values

| Platform | Host                   | Region  |
| --- |------------------------|---------|
| BR1 | br1.api.riotgames.com  | Brazil |
| EUN1 | eun1.api.riotgames.com | Europe Nordic & East |
| EUW1 | euw1.api.riotgames.com | Europe West |
| JP1 | jp1.api.riotgames.com  | Japan | 
| KR | kr.api.riotgames.com   | Korea |
| LA1 | la1.api.riotgames.com  | Latin America North |
| LA2 | la2.api.riotgames.com  | Lation America South |
| NA1 | na1.api.riotgames.com  | North America |
| OC1 | oc1.api.riotgames.com  | Oceania |
| TR1 | tr1.api.riotgames.com  | Turkiye |
| RU | ru.api.riotgames.com   | Russia |
| PH2 | ph2.api.riotgames.com  | Philippines |
| SG2 | sg2.api.riotgames.com  | Singapore |
| TH2 | th2.api.riotgames.com  | Thailand |
| TW2 | tw2.api.riotgames.com  | Taiwan, HongKong, Macao |
| VN2 | vn2.api.riotgames.com  | Vietnam |

---

# Research Proposal
Research Proposal:
Title: Federated Learning for Cheat Detection in Online Games: Adaptive Model Fusion Based on League of Legends Player Behavior

Cheating in competitive online games such as League of Legends poses a significant threat to fair play and undermines e-sports integrity. This project investigates how federated learning (FL) can enable distributed cheat detection without compromising player privacy. The proposed approach is inspired by the FedFusion approach fraud detection, the goal of which is to implement adaptive model fusion to behavioural gameplay data.

The proposed model conceptualises each game server as a federated client that trains its own classifier based on features such as APM, spell usage, and movement timing. These features are extracted via the Riot Games API. The presence of gameplay variations across servers can result in discrepancies in features, which are addressed through the implementation of adaptive fusion techniques.

The architecture includes an adjustable fusion parameter (α) to achieve a balance local and global learning. Optional extensions involve the implementation of reinforcement learning for α-optimization, as proposed in the FedFusion paper, and visualization tools like t-SNE and SHAP to detect patterns and explain decisions.

The project's objective is threefold: firstly, to evaluate the method's accuracy, robustness, and generalizability to other games in League of Legends; secondly, to consider the ethical, legal, and privacy implications (e.g., GDPR); and thirdly, to explore the potential for extending the method to other games. The project's overarching objective is to explore scalable and privacy-preserving approaches to cheat detection in modern online games.

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






