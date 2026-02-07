import pandas as pd

df = pd.read_csv("clean_orders_num.csv")

# Basic checks
print("Rows:", len(df))
print(df[["sales_num", "profit_num", "quantity_num", "discount_num"]].describe())

# Executive KPIs
total_revenue = df["sales_num"].sum()
total_profit = df["profit_num"].sum()
margin = (total_profit / total_revenue) * 100

orders = df["Order ID"].nunique()
customers = df["Customer ID"].nunique()
products = df["Product Name"].nunique()

print("\nEXECUTIVE KPI SNAPSHOT")
print(f"Total revenue: ${total_revenue:,.2f}")
print(f"Total profit:  ${total_profit:,.2f}")
print(f"Margin:        {margin:.2f}%")
print(f"Orders:        {orders:,}")
print(f"Customers:     {customers:,}")
print(f"Products:      {products:,}")

# Profit concentration (Power Move)
prod_profit = (df.groupby("Product Name", as_index=False)
                 .agg(revenue=("sales_num","sum"), profit=("profit_num","sum"))
                 .sort_values("profit", ascending=False))

prod_profit["profit_share"] = prod_profit["profit"] / prod_profit["profit"].sum()
prod_profit["cum_profit_share"] = prod_profit["profit_share"].cumsum()
prod_profit["rank"] = range(1, len(prod_profit) + 1)

# How many products generate 80% of profit?
top80 = prod_profit[prod_profit["cum_profit_share"] <= 0.80]
pct_products_for_80 = (len(top80) / len(prod_profit)) * 100

print("\nPROFIT CONCENTRATION")
print(f"Products needed for 80% of profit: {len(top80):,} "
      f"({pct_products_for_80:.2f}% of products)")

# Customer risk scoring (simple + explainable)
cust = (df.groupby("Customer ID", as_index=False)
          .agg(revenue=("sales_num","sum"),
               profit=("profit_num","sum"),
               orders=("Order ID","nunique"),
               avg_discount=("discount_num","mean")))

cust["margin_pct"] = (cust["profit"] / cust["revenue"]) * 100
cust["risk_flag"] = (cust["profit"] < 0) | (cust["margin_pct"] < 0)

worst_customers = cust.sort_values("profit").head(20)
print("\nWORST 20 CUSTOMERS BY PROFIT")
print(worst_customers.to_string(index=False))

# Save outputs for Tableau / README
prod_profit.head(50).to_csv("top_50_products_by_profit.csv", index=False)
worst_customers.to_csv("worst_20_customers.csv", index=False)
cust.sort_values("margin_pct").to_csv("customer_risk_table.csv", index=False)

print("\nSaved:")
print("- top_50_products_by_profit.csv")
print("- worst_20_customers.csv")
print("- customer_risk_table.csv")
