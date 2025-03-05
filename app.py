from flask import Flask, render_template, request
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)

# Full ETF database
etf_database = {
    "VTI": {"name": "Vanguard Total Stock Market ETF", "type": "Equity", "expense_ratio": 0.03,
            "returns": {"1yr": 18.0, "3yr": 9.0, "5yr": 13.5, "10yr": 12.5, "2020": 20.9, "2021": 25.7, "2022": -19.5, "2023": 26.1, "2024": 15.0}},
    "QQQ": {"name": "Invesco QQQ Trust", "type": "Equity", "expense_ratio": 0.20,
            "returns": {"1yr": 28.0, "3yr": 10.5, "5yr": 19.0, "10yr": 17.0, "2020": 48.6, "2021": 27.4, "2022": -32.6, "2023": 54.9, "2024": 20.0}},
    "BND": {"name": "Vanguard Total Bond Market ETF", "type": "Bond", "expense_ratio": 0.035,
            "returns": {"1yr": 6.0, "3yr": -1.5, "5yr": 1.0, "10yr": 2.0, "2020": 7.7, "2021": -1.9, "2022": -13.1, "2023": 5.7, "2024": 4.5}},
    "ICLN": {"name": "iShares Global Clean Energy ETF", "type": "Equity", "expense_ratio": 0.46,
            "returns": {"1yr": 10.0, "3yr": -5.0, "5yr": 12.0, "10yr": 9.0, "2020": 141.0, "2021": -20.5, "2022": -11.0, "2023": -20.8, "2024": 8.0}},
    "VGT": {"name": "Vanguard Information Technology ETF", "type": "Equity", "expense_ratio": 0.10,
            "returns": {"1yr": 30.0, "3yr": 12.0, "5yr": 20.5, "10yr": 18.5, "2020": 46.0, "2021": 30.5, "2022": -29.7, "2023": 52.7, "2024": 22.0}},
    "XLK": {"name": "Technology Select Sector SPDR Fund", "type": "Equity", "expense_ratio": 0.13,
            "returns": {"1yr": 29.0, "3yr": 13.0, "5yr": 21.0, "10yr": 19.0, "2020": 43.6, "2021": 34.5, "2022": -27.9, "2023": 55.9, "2024": 21.0}},
    "VNQ": {"name": "Vanguard Real Estate ETF", "type": "Equity", "expense_ratio": 0.12,
            "returns": {"1yr": 12.0, "3yr": 3.5, "5yr": 6.0, "10yr": 6.8, "2020": -4.7, "2021": 40.4, "2022": -26.2, "2023": 11.8, "2024": 10.0}},
    "GLD": {"name": "SPDR Gold Shares", "type": "Commodity", "expense_ratio": 0.40,
            "returns": {"1yr": 15.0, "3yr": 8.0, "5yr": 10.0, "10yr": 5.5, "2020": 24.8, "2021": -4.2, "2022": -0.8, "2023": 13.1, "2024": 14.0}},
    "XLV": {"name": "Health Care Select Sector SPDR Fund", "type": "Equity", "expense_ratio": 0.13,
            "returns": {"1yr": 10.0, "3yr": 7.5, "5yr": 11.0, "10yr": 10.5, "2020": 13.4, "2021": 26.1, "2022": -2.0, "2023": 2.1, "2024": 8.0}},
    "XLE": {"name": "Energy Select Sector SPDR Fund", "type": "Equity", "expense_ratio": 0.13,
            "returns": {"1yr": 15.0, "3yr": 20.0, "5yr": 9.5, "10yr": 5.0, "2020": -33.7, "2021": 53.3, "2022": 64.2, "2023": -1.0, "2024": 12.0}},
    "XLF": {"name": "Financial Select Sector SPDR Fund", "type": "Equity", "expense_ratio": 0.13,
            "returns": {"1yr": 22.0, "3yr": 7.0, "5yr": 10.0, "10yr": 9.5, "2020": -1.7, "2021": 35.0, "2022": -10.6, "2023": 12.0, "2024": 18.0}},
    "XLI": {"name": "Industrial Select Sector SPDR Fund", "type": "Equity", "expense_ratio": 0.13,
            "returns": {"1yr": 18.0, "3yr": 9.0, "5yr": 11.5, "10yr": 10.0, "2020": 11.0, "2021": 21.4, "2022": -5.5, "2023": 18.0, "2024": 14.0}},
    "XLP": {"name": "Consumer Staples Select Sector SPDR Fund", "type": "Equity", "expense_ratio": 0.13,
            "returns": {"1yr": 8.0, "3yr": 5.5, "5yr": 8.0, "10yr": 7.5, "2020": 10.1, "2021": 17.2, "2022": -0.8, "2023": 0.5, "2024": 6.0}},
    "XLY": {"name": "Consumer Discretionary Select Sector SPDR Fund", "type": "Equity", "expense_ratio": 0.13,
            "returns": {"1yr": 12.0, "3yr": 4.0, "5yr": 11.5, "10yr": 12.0, "2020": 29.6, "2021": 24.8, "2022": -36.2, "2023": 40.0, "2024": 10.0}},
    "TIP": {"name": "iShares TIPS Bond ETF", "type": "Bond", "expense_ratio": 0.19,
            "returns": {"1yr": 5.0, "3yr": 0.0, "5yr": 2.8, "10yr": 2.2, "2020": 11.0, "2021": 5.7, "2022": -11.9, "2023": 3.9, "2024": 4.0}},
    "AGG": {"name": "iShares Core U.S. Aggregate Bond ETF", "type": "Bond", "expense_ratio": 0.04,
            "returns": {"1yr": 6.5, "3yr": -1.0, "5yr": 1.2, "10yr": 2.1, "2020": 7.5, "2021": -1.6, "2022": -13.0, "2023": 5.5, "2024": 5.0}}
}

# Keyword mappings
sector_keywords = {
    "tech": ["tech", "technology", "it", "software", "hardware"],
    "green": ["green", "clean", "renewable", "sustainable", "environment", "environmental", "energy"],
    "real estate": ["real estate", "property", "housing", "realty"],
    "healthcare": ["healthcare", "health", "medical", "pharma", "pharmaceutical"],
    "finance": ["finance", "financial", "banking", "investment", "money"]
}

goal_keywords = {
    "retirement": ["retirement", "retire", "pension", "old age"],
    "house": ["house", "home", "mortgage", "property"],
    "education": ["education", "school", "college", "university", "tuition"],
    "car": ["car", "vehicle", "auto", "automobile"],
    "travel": ["travel", "vacation", "trip", "holiday"],
    "emergency": ["emergency", "emergency fund", "rainy day", "safety net"],
    "business": ["business", "startup", "company", "venture"],
    "wedding": ["wedding", "marriage", "ceremony"],
    "wealth": ["wealth", "growth", "grow", "long-term"]
}

def parse_goals(sentence):
    sentence = sentence.lower()
    detected_goals = [goal for goal, keywords in goal_keywords.items() if any(k in sentence for k in keywords)]
    return detected_goals if detected_goals else ["general savings"]

def parse_interests(sentence):
    sentence = sentence.lower()
    detected_interests = [sector for sector, keywords in sector_keywords.items() if any(k in sentence for k in keywords)]
    return detected_interests if detected_interests else ["default"]

def build_portfolio(user_data):
    amount = float(user_data["amount"])
    horizon = int(user_data["horizon"])
    interests = user_data["interests"]
    risk = user_data["risk"]
    invest_goal = user_data["invest_goal"]

    # Base equity/bond split based on risk
    if risk == "high":
        if horizon >= 15:
            equity_percent = 0.90
            bond_percent = 0.10
        elif horizon >= 7:
            equity_percent = 0.75
            bond_percent = 0.25
        else:
            equity_percent = 0.50
            bond_percent = 0.50
    elif risk == "medium":
        if horizon >= 15:
            equity_percent = 0.80
            bond_percent = 0.20
        elif horizon >= 7:
            equity_percent = 0.65
            bond_percent = 0.35
        else:
            equity_percent = 0.40
            bond_percent = 0.60
    else:  # Low risk
        if horizon >= 15:
            equity_percent = 0.60
            bond_percent = 0.40
        elif horizon >= 7:
            equity_percent = 0.50
            bond_percent = 0.50
        else:
            equity_percent = 0.30
            bond_percent = 0.70

    # Adjust based on investment goal
    if invest_goal == "preservation":
        equity_percent *= 0.8
        bond_percent = 1 - equity_percent
    elif invest_goal == "income":
        equity_percent *= 0.9
        bond_percent = 1 - equity_percent

    portfolio = {}
    equity_amount = amount * equity_percent
    bond_amount = amount * bond_percent

    # Handle multiple interests
    if len(interests) > 1 and "default" not in interests:
        equity_split = 1.0 / len(interests)
        for interest in interests:
            if interest == "tech":
                portfolio["QQQ"] = portfolio.get("QQQ", 0) + equity_amount * equity_split * (0.45 if invest_goal == "growth" else 0.35)
                portfolio["VGT"] = portfolio.get("VGT", 0) + equity_amount * equity_split * 0.25
                portfolio["XLK"] = portfolio.get("XLK", 0) + equity_amount * equity_split * 0.20
                portfolio["VTI"] = portfolio.get("VTI", 0) + equity_amount * equity_split * (0.10 if invest_goal == "growth" else 0.20)
            elif interest == "green":
                portfolio["ICLN"] = portfolio.get("ICLN", 0) + equity_amount * equity_split * (0.50 if invest_goal == "growth" else 0.40)
                portfolio["XLE"] = portfolio.get("XLE", 0) + equity_amount * equity_split * 0.25
                portfolio["VTI"] = portfolio.get("VTI", 0) + equity_amount * equity_split * 0.25
                portfolio["GLD"] = portfolio.get("GLD", 0) + equity_amount * equity_split * 0.10
            elif interest == "real estate":
                portfolio["VNQ"] = portfolio.get("VNQ", 0) + equity_amount * equity_split * (0.60 if invest_goal == "income" else 0.50)
                portfolio["VTI"] = portfolio.get("VTI", 0) + equity_amount * equity_split * 0.30
                portfolio["XLF"] = portfolio.get("XLF", 0) + equity_amount * equity_split * 0.20
            elif interest == "healthcare":
                portfolio["XLV"] = portfolio.get("XLV", 0) + equity_amount * equity_split * 0.45
                portfolio["VTI"] = portfolio.get("VTI", 0) + equity_amount * equity_split * 0.35
                portfolio["XLP"] = portfolio.get("XLP", 0) + equity_amount * equity_split * 0.20
            elif interest == "finance":
                portfolio["XLF"] = portfolio.get("XLF", 0) + equity_amount * equity_split * 0.40
                portfolio["VTI"] = portfolio.get("VTI", 0) + equity_amount * equity_split * 0.40
                portfolio["GLD"] = portfolio.get("GLD", 0) + equity_amount * equity_split * 0.20
    else:
        interest = interests[0]
        if interest == "tech":
            portfolio["QQQ"] = equity_amount * (0.45 if invest_goal == "growth" else 0.35)
            portfolio["VGT"] = equity_amount * 0.25
            portfolio["XLK"] = equity_amount * 0.20
            portfolio["VTI"] = equity_amount * (0.10 if invest_goal == "growth" else 0.20)
        elif interest == "green":
            portfolio["ICLN"] = equity_amount * (0.50 if invest_goal == "growth" else 0.40)
            portfolio["XLE"] = equity_amount * 0.25
            portfolio["VTI"] = equity_amount * 0.25
            portfolio["GLD"] = equity_amount * 0.10
        elif interest == "real estate":
            portfolio["VNQ"] = equity_amount * (0.60 if invest_goal == "income" else 0.50)
            portfolio["VTI"] = equity_amount * 0.30
            portfolio["XLF"] = equity_amount * 0.20
        elif interest == "healthcare":
            portfolio["XLV"] = equity_amount * 0.45
            portfolio["VTI"] = equity_amount * 0.35
            portfolio["XLP"] = equity_amount * 0.20
        elif interest == "finance":
            portfolio["XLF"] = equity_amount * 0.40
            portfolio["VTI"] = equity_amount * 0.40
            portfolio["GLD"] = equity_amount * 0.20
        else:  # Default
            portfolio["VTI"] = equity_amount * 0.50
            portfolio["XLY"] = equity_amount * 0.20
            portfolio["XLI"] = equity_amount * 0.20
            portfolio["GLD"] = equity_amount * 0.10

    if bond_amount > 0:
        portfolio["BND"] = bond_amount * (0.70 if invest_goal == "income" else 0.60)
        portfolio["TIP"] = bond_amount * (0.30 if invest_goal == "income" else 0.40)

    return portfolio

def generate_pie_chart(portfolio):
    plt.figure(figsize=(6, 6))
    labels = [f"{etf} (${value:.2f})" for etf, value in portfolio.items()]
    sizes = list(portfolio.values())
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title("Portfolio Allocation")
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return f"data:image/png;base64,{plot_url}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        age = int(request.form['age'])
        goals_input = request.form['goals']
        horizon = int(request.form['horizon'])
        interests_input = request.form['interests']
        stated_risk = request.form['stated_risk'].lower()
        q1 = int(request.form['q1'])
        q2 = int(request.form['q2'])
        invest_goal = request.form['invest_goal'].lower()
        amount = float(request.form['amount'])
        monthly = float(request.form['monthly'])

        goals = parse_goals(goals_input)
        interests = parse_interests(interests_input)
        if "retirement" in goals:
            retirement_horizon = max(65 - age, 5)
            horizon = min(horizon, retirement_horizon)
        risk_score = q1 + q2
        behavioral_risk = "low" if risk_score <= 6 else "medium" if risk_score <= 13 else "high"
        final_risk = stated_risk if stated_risk == behavioral_risk else "medium" if (stated_risk == "high" and behavioral_risk == "low") or (stated_risk == "low" and behavioral_risk == "high") else behavioral_risk

        user_data = {
            "goals": goals,
            "interests": interests,
            "risk": final_risk,
            "horizon": horizon,
            "amount": amount,
            "monthly": monthly,
            "invest_goal": invest_goal,
            "age": age
        }
        portfolio = build_portfolio(user_data)
        pie_chart = generate_pie_chart(portfolio)
        portfolio_total = sum(portfolio.values())

        return render_template('result.html', user_data=user_data, portfolio=portfolio, pie_chart=pie_chart, portfolio_total=portfolio_total, etf_database=etf_database)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)