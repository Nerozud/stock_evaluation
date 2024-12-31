import yfinance as yf


def evaluate_stock(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)

    try:
        # Get current stock price
        hist = ticker.history(period="1d")
        if hist.empty:
            print("Failed to retrieve stock price data.")
            return
        current_price = hist["Close"].iloc[0]

        # Get EPS from the company's financial information
        info = ticker.info
        eps = info.get("trailingEps", None)

        # Get shares outstanding
        shares_outstanding = info.get("sharesOutstanding", None)
        if shares_outstanding is None:
            print("Not enough financial data to calculate EPS.")
            return

        # ----------------------------------
        # Process Annual Data
        # ----------------------------------
        financials_annual = ticker.financials  # Annual financial statements

        if financials_annual.empty or eps is None:
            print("Not enough annual financial data to calculate the fair value.")
            return

        # Extract net income over the years (annual)
        net_income_annual = financials_annual.loc["Net Income"]

        # Reverse the series to have oldest to newest
        net_income_annual = net_income_annual[::-1]

        # Calculate EPS for each year
        eps_history_annual = net_income_annual / shares_outstanding

        # Remove any periods where EPS <= 0
        eps_history_annual = eps_history_annual[eps_history_annual > 0]

        if len(eps_history_annual) < 2:
            print("Not enough historical annual EPS data to calculate growth rate.")
            return

        # Calculate CAGR of EPS (Annual)
        eps_start_annual = eps_history_annual.iloc[0]
        eps_end_annual = eps_history_annual.iloc[-1]
        num_years_annual = (
            len(eps_history_annual) - 1
        )  # Number of years between data points

        growth_rate_annual = (
            (eps_end_annual / eps_start_annual) ** (1 / num_years_annual)
        ) - 1

        growth_rate_percentage_annual = growth_rate_annual * 100

        # Calculate the fair value using the Graham formula (Annual)
        fair_value_annual = eps * (
            7 + 1.5 * growth_rate_percentage_annual
        )  # Adjusted Graham formula

        # Determine if the stock is cheap or expensive based on annual data
        if current_price < fair_value_annual * 0.8:
            valuation_annual = "cheap"
        elif current_price > fair_value_annual * 1.2:
            valuation_annual = "expensive"
        else:
            valuation_annual = "fairly valued"

        # ----------------------------------
        # Process Quarterly Data
        # ----------------------------------
        financials_quarterly = (
            ticker.quarterly_financials
        )  # Quarterly financial statements

        if financials_quarterly.empty:
            print("Not enough quarterly financial data to calculate the fair value.")
            return

        # Extract net income over the quarters
        net_income_quarterly = financials_quarterly.loc["Net Income"]

        # Reverse the series to have oldest to newest
        net_income_quarterly = net_income_quarterly[::-1]

        # Calculate EPS for each quarter
        eps_history_quarterly = net_income_quarterly / shares_outstanding

        # Remove any periods where EPS <= 0
        eps_history_quarterly = eps_history_quarterly[eps_history_quarterly > 0]

        if len(eps_history_quarterly) < 2:
            print("Not enough historical quarterly EPS data to calculate growth rate.")
            return

        # Calculate CAGR of EPS (Quarterly)
        eps_start_quarterly = eps_history_quarterly.iloc[0]
        eps_end_quarterly = eps_history_quarterly.iloc[-1]
        num_years_quarterly = (
            len(eps_history_quarterly) / 4
        )  # Convert quarters to years

        growth_rate_quarterly = (
            (eps_end_quarterly / eps_start_quarterly) ** (1 / num_years_quarterly)
        ) - 1

        growth_rate_percentage_quarterly = growth_rate_quarterly * 100

        # Calculate the fair value using the Graham formula (Quarterly)
        fair_value_quarterly = eps * (
            7 + 1.5 * growth_rate_percentage_quarterly
        )  # Adjusted Graham formula

        # Determine if the stock is cheap or expensive based on quarterly data
        if current_price < fair_value_quarterly * 0.8:
            valuation_quarterly = "cheap"
        elif current_price > fair_value_quarterly * 1.2:
            valuation_quarterly = "expensive"
        else:
            valuation_quarterly = "fairly valued"

        # ----------------------------------
        # Output the evaluation
        # ----------------------------------
        print(f"\nTicker: {ticker_symbol}")
        print(f"Current Price: ${current_price:.2f}")
        print(f"EPS (Trailing): ${eps:.2f}")

        print("\n--- Based on Annual Data ---")
        print(
            f"Calculated Annual EPS Growth Rate: {growth_rate_percentage_annual:.2f}%"
        )
        print(f"Calculated Fair Value (Annual): ${fair_value_annual:.2f}")
        print(
            f"The stock is considered **{valuation_annual.upper()}** compared to its fair value (Annual)."
        )

        print("\n--- Based on Quarterly Data ---")
        print(
            f"Calculated Quarterly EPS Growth Rate: {growth_rate_percentage_quarterly:.2f}%"
        )
        print(f"Calculated Fair Value (Quarterly): ${fair_value_quarterly:.2f}")
        print(
            f"The stock is considered **{valuation_quarterly.upper()}** compared to its fair value (Quarterly)."
        )

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    while True:
        symbol = input(
            "Enter the ticker symbol of the company (or 'exit' to quit): "
        ).upper()
        if symbol == "EXIT":
            break
        evaluate_stock(symbol)
