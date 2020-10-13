#pgadmin 4 Client table Column creation
ALTER TABLE public."Client"
	ADD COLUMN "Base Number" VARCHAR(32),
	ADD COLUMN "Client Name" VARCHAR(16),
    	ADD COLUMN "Position As of Date" VARCHAR(50),
	ADD COLUMN "Asset Class" VARCHAR(50),
	ADD COLUMN "Asset Sub Class" VARCHAR(50),
	ADD COLUMN "Name" VARCHAR(100),
	ADD COLUMN "Ticker" VARCHAR(50),
	ADD COLUMN "CCY" VARCHAR(3),
	ADD COLUMN "Nominal Units" VARCHAR(50),
	ADD COLUMN "Nominal Amount (CCY)" VARCHAR(50),
	ADD COLUMN "Nominal Amount (USD)" VARCHAR(50),
	ADD COLUMN "Loan / Cash Rate to client" VARCHAR(50),
	ADD COLUMN "% Change from Avg Cost" VARCHAR(50),
	ADD COLUMN "Current Price" VARCHAR(50),
	ADD COLUMN "Closing Price" VARCHAR(50),
	ADD COLUMN "Average Cost" VARCHAR(50),
	ADD COLUMN "YTD%" VARCHAR(50),
	ADD COLUMN "1d %" VARCHAR(50),
	ADD COLUMN "5d %" VARCHAR(50),
	ADD COLUMN "1m %" VARCHAR(50),
	ADD COLUMN "6m %" VARCHAR(50),
	ADD COLUMN "12m %" VARCHAR(50),
	ADD COLUMN "Company Description" VARCHAR(1000),
	ADD COLUMN "Citi rating" VARCHAR(50),
	ADD COLUMN "Citi TARGET" VARCHAR(50),
	ADD COLUMN "% to target" VARCHAR(50),
	ADD COLUMN "Market Consensus" VARCHAR(50),
	ADD COLUMN "12M Div Yield (%)" VARCHAR(50),
	ADD COLUMN "Dividend EX Date" VARCHAR(50),
	ADD COLUMN "P/E Ratio" VARCHAR(50),
	ADD COLUMN "P/B Ratio" VARCHAR(50),
	ADD COLUMN "EPS (Current Year)" VARCHAR(50),
	ADD COLUMN "EPS (Next Year)" VARCHAR(50),
	ADD COLUMN "YoY EPS Growth (%)" VARCHAR(50),
	ADD COLUMN "50D MA" VARCHAR(50),
	ADD COLUMN "200D MA" VARCHAR(50),
	ADD COLUMN "Profit Margin" VARCHAR(50),
	ADD COLUMN "Sector" VARCHAR(50),
	ADD COLUMN "Country (Domicile)" VARCHAR(50),
	ADD COLUMN "Region (Largest Revenue)" VARCHAR(50),
	ADD COLUMN "Rank" VARCHAR(50),
	ADD COLUMN "Moodys R" VARCHAR(50),
	ADD COLUMN "S&P R" VARCHAR(50),
	ADD COLUMN "Fitch" VARCHAR(50),
	ADD COLUMN "Coupon" VARCHAR(50),
	ADD COLUMN "YTC" VARCHAR(50),
	ADD COLUMN "YTM" VARCHAR(50),
	ADD COLUMN "Coupon type" VARCHAR(50),
	ADD COLUMN "Issue Date" VARCHAR(50),
	ADD COLUMN "Maturity" VARCHAR(50),
	ADD COLUMN "Next Call Date" VARCHAR(50),
	ADD COLUMN "Commitment Amount" VARCHAR(50),
	ADD COLUMN "Contribution Amount" VARCHAR(50),
	ADD COLUMN "Outstanding Commitment" VARCHAR(50),
	ADD COLUMN "% Outstanding Amount" VARCHAR(50),
	ADD COLUMN "Distribution Amount" VARCHAR(50),
	ADD COLUMN "Return on Contribution" VARCHAR(50),
	ADD COLUMN "Trade Number" VARCHAR(300),
	ADD COLUMN "Exchange Rate (CCY to USD)" VARCHAR(50),
	ADD COLUMN "Latest Nominal Amount (USD)" VARCHAR(50),
	ADD COLUMN "Estimated Original Amount Paid" VARCHAR(50),
	ADD COLUMN "Estimated Profit/Loss" VARCHAR(50),
	ADD COLUMN "% Profit/Loss Return" VARCHAR(300),
	ADD COLUMN "Target Risk Level" VARCHAR(5);

#pgadmin 4 RiskAllocation table Column creation
ALTER TABLE public."RiskAllocation"
	ADD COLUMN "Asset Class" VARCHAR(32),
	ADD COLUMN "Breakdown by Percentage" VARCHAR(10),
    	ADD COLUMN "Level" VARCHAR(50);

INSERT INTO public."RiskAllocation"(
	"Asset Class", "Breakdown by Percentage", "Level")
	VALUES ('CASH', '6', '1'),
			('FIXED INCOME', '94', '1'),
			('EQUITIES', '0', '1'),
			('CASH', '4', '2'),
			('FIXED INCOME' , '66', '2'),
			('EQUITIES', '30', '2'),
			('CASH', '2', '3'),
			('FIXED INCOME', '37.5', '3'),
			('EQUITIES', '60.5', '3'),
			('CASH', '2', '4'),
			('FIXED INCOME', '19', '4'),
			('EQUITIES', '79', '4'),
			('CASH', '0', '5'),
			('FIXED INCOME', '0', '5'),
			('EQUITIES', '100', '5');

#psql import to local
\copy public."Client" ("Base Number", "Position As of Date", "Client Name", "Asset Class", "Asset Sub Class", "Name", "Ticker", "CCY", "Nominal Units", "Nominal Amount (CCY)", "Nominal Amount (USD)", "Loan / Cash Rate to client", "% Change from Avg Cost", "Current Price", "Closing Price", "Average Cost", "YTD%", "1d %", "5d %", "1m %", "6m %","12m %", "Company Description", "Citi rating", "Citi TARGET", "% to target", "Market Consensus", "12M Div Yield (%)", "Dividend EX Date", "P/E Ratio", "P/B Ratio", "EPS (Current Year)", "EPS (Next Year)", "YoY EPS Growth (%)", "50D MA", "200D MA", "Profit Margin", "Sector", "Country (Domicile)", "Region (Largest Revenue)", "Rank", "Moodys R", "S&P R", "Fitch", "Coupon", "YTC", "YTM", "Coupon type", "Issue Date", "Maturity", "Next Call Date", "Commitment Amount", "Contribution Amount", "Outstanding Commitment", "% Outstanding Amount","Distribution Amount", "Return on Contribution", "Trade Number", "Exchange Rate (CCY to USD)", "Latest Nominal Amount (USD)", "Estimated Original Amount Paid", "Estimated Profit/Loss", "% Profit/Loss Return", "Target Risk Level") FROM 'C:/Users/Harvey/Desktop/FYP-IS~1/Harvey/Client.csv' DELIMITER ',' CSV HEADER

#Export dump file from local
pg_dump -Fc --no-acl --no-owner -h localhost -U postgres postgres > mydb.dump

#Import dump file to Heroku postgreSQL (Double quotes in bucket url is important)
heroku pg:backups:restore "https://mydbfin.s3.amazonaws.com/mydb+v4.sql" DATABASE_URL

