import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UsageQuotasCard } from "@/components/usage-quotas-card";

describe("UsageQuotasCard", () => {
  it("renders exceeded quotas", () => {
    const { container } = render(
      <UsageQuotasCard plan="free" anyExceeded={true} upgradeSuggested={true} checks={[
        { resource: "api_calls", used: 1200, limit: 1000, pct: 120, exceeded: true },
        { resource: "apps", used: 2, limit: 3, pct: 66.7, exceeded: false },
      ]} />
    );
    expect(container.textContent).toContain("Usage Quotas");
    expect(container.textContent).toContain("free");
    expect(container.textContent).toContain("API Calls");
    expect(container.textContent).toContain("1,200");
    expect(container.textContent).toContain("upgrading");
  });
});
