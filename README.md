# China A‑Share Analysis Tool + Financial Term AI Explainer

**Track 4 – Interactive Data Analysis Tool**  
*ACC102 Mini Assignment | April 2026*

## 1. Problem & Target User

**Problem:** Stock market is intimidating for beginners – they don’t understand valuation, technical signals, or financial jargon.

**Target User:** Investment novices who want to explore A‑share data with simple visualisations and plain‑language explanations.

## 2. Data Source

- **CSMAR database** (China Stock Market & Accounting Research)
- Files used: `TRD_Dalyr.xlsx` (daily trading data)
- Access date: 20 April 2026
- **Note:** The data files are included in this repository (<25 MB). If you clone the repo, they are ready to use.

## 3. Methods (Python Workflow)

- **Data loading & cleaning:** `pandas` reads Excel, standardises column names, parses dates.
- **Technical indicators:** MA5, MA20, RSI, 20‑day momentum, cumulative return.
- **Valuation thermometer:** Historical price percentile (30/70 thresholds).
- **Buy/sell signals:** Combination of trend (MA cross), RSI (oversold/overbought), and price vs MA20.
- **Portfolio recommendation:** Risk profile assessment (questionnaire) + scoring based on return, volatility, drawdown.
- **AI term explainer:** Calls DeepSeek API (OpenAI‑compatible) to translate financial jargon into everyday language.

## 4. How to Run (Local)

1. **Clone the repository**  
   `git clone https://gitee.com/emmayuan20/acc102.git`

2. **Install dependencies**  
   `pip install -r requirements.txt`


3. **Run the app**  
   `streamlit run app101.py`

4. **Use the tool**  
   - Complete the risk assessment in sidebar.  
   - Select stocks → click “Load Data”.  
   - Explore valuation thermometer, signals, charts, and portfolio recommendations.  
   - Scroll down to the AI explainer and type any financial term.

## 5. Product Links

- **Gitee repository (code + README):** [https://gitee.com/emmayuan20/acc102](https://gitee.com/emmayuan20/acc102)
- **Demo video:** [  ]

## 6. Demo Video (1‑3 minutes)

[  ]

## 7. Limitations & Next Steps

- **Data freshness:** Uses local CSMAR export; does not auto‑update.
- **No volume data:** Signals rely only on price & returns.
- **API dependency:** AI explainer requires DeepSeek API key and balance.
- **Simplified signals:** Real‑world trading needs more factors (volume, news, sector).
- **Next steps:** Add volume indicators, support real‑time API (e.g., Yahoo Finance).

## 8. AI Disclosure

- **DeepSeek API** (deepseek-chat model, accessed 21 April 2026): Used to generate plain‑language explanations of financial terms.
- **ChatGPT (GPT‑4, April 2026):** Assisted in writing Streamlit layout code, debugging encoding issues.
