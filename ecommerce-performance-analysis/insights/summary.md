# Summary Insights (Amazon-Style)

## What I Did
Using Google BigQuery, I cleaned and analyzed an eCommerce transaction dataset to evaluate
SKU-level performance, assess revenue concentration, and flag potential product risks.
The analysis is designed to mirror typical “Amazon channel” analytics work: reliable reporting,
merchandising-ready rankings, and explainable risk signals.

---

## Key Results

### 1) Top Products by Revenue (Merchandising View)
After excluding non-merchandise entries (e.g., postage/manual adjustments), the highest-revenue
products included:

- REGENCY CAKESTAND 3 TIER (SKU 22423)
- PAPER CRAFT, LITTLE BIRDIE (SKU 23843)
- WHITE HANGING HEART T-LIGHT HOLDER (SKU 85123A)
- PARTY BUNTING (SKU 47566)
- JUMBO BAG RED RETROSPOT (SKU 85099B)

These products combine strong revenue with high unit volume, making them priority SKUs for
merchandising and inventory planning.

---

### 2) Revenue Concentration
Revenue was broadly distributed across the catalog.

- **Top 10 SKUs revenue:** 968,148.41
- **Total revenue:** 10,304,221.07
- **% of revenue from Top 10 SKUs:** **9.4%**

This indicates low concentration risk and a diversified product mix.

---

### 3) Decline Risk Flags (Recent vs Historical)
To flag potential risks, I compared each SKU’s average monthly revenue to its average revenue
over the most recent 3 months. Several SKUs showed notable recent softening, including both
mid-tier products and at least one historically strong SKU, reinforcing the need for ongoing
performance monitoring.

---

## Notes on Data Cleaning
To align with standard eCommerce performance reporting:
- Excluded canceled invoices (Invoice starting with “C”)
- Excluded returns (negative quantities) by filtering to `quantity > 0`
- Removed non-sensical pricing by filtering to `unit_price > 0`
- Created `revenue = quantity * unit_price` and extracted year/month for reporting

---

## Deliverables
- SQL cleaning script creating an analysis-ready table in BigQuery
- Top-SKU ranking queries (raw + merch-ready filtered)
- Revenue concentration measurement (Top 10 share)
- SKU decline flag query (recent vs historical performance)
