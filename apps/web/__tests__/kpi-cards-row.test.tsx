import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { KpiCardsRow } from "@/components/kpi-cards-row";

describe("KpiCardsRow", () => {
  it("renders KPIs", () => {
    const { container } = render(
      <KpiCardsRow cards={[
        { key: "mrr", label: "MRR", icon: "💰", display: "$50,000", deltaDisplay: "+11.1%", trend: "up", positive: true },
        { key: "churn", label: "Churn Rate", icon: "📉", display: "2.5%", deltaDisplay: "-16.7%", trend: "down", positive: true },
      ]} />
    );
    expect(container.textContent).toContain("$50,000");
    expect(container.textContent).toContain("MRR");
    expect(container.textContent).toContain("+11.1%");
    expect(container.textContent).toContain("2.5%");
    expect(container.textContent).toContain("Churn Rate");
  });
});
