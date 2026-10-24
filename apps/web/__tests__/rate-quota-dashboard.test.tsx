import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RateQuotaDashboard } from "@/components/rate-quota-dashboard";

describe("RateQuotaDashboard", () => {
  it("renders quotas", () => {
    const { container } = render(
      <RateQuotaDashboard healthy={1} atRisk={1} exhausted={1}
        quotas={[
          { name: "API calls", used: 450, limit: 1000, pctUsed: 45, status: "healthy", remaining: 550 },
          { name: "Storage", used: 900, limit: 1000, pctUsed: 90, status: "at_risk", remaining: 100 },
          { name: "Webhooks", used: 50, limit: 50, pctUsed: 100, status: "exhausted", remaining: 0 },
        ]} />
    );
    expect(container.textContent).toContain("Quota Dashboard");
    expect(container.textContent).toContain("1 ok");
    expect(container.textContent).toContain("1 at risk");
    expect(container.textContent).toContain("1 exhausted");
    expect(container.textContent).toContain("API calls");
    expect(container.textContent).toContain("450/1000");
  });
});
