import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { QuotaEnforcePanel } from "@/components/quota-enforce-panel";

describe("QuotaEnforcePanel", () => {
  it("renders", () => {
    const { container } = render(
      <QuotaEnforcePanel exceeded={1} warnings={1} actionNeeded={true}
        quotas={[
          { resource: "api_calls", current: 50, limit: 100, pctUsed: 50, exceeded: false, warning: false },
          { resource: "storage", current: 90, limit: 100, pctUsed: 90, exceeded: false, warning: true },
          { resource: "bandwidth", current: 110, limit: 100, pctUsed: 110, exceeded: true, warning: false },
        ]} />
    );
    expect(container.textContent).toContain("Quota Enforcement");
    expect(container.textContent).toContain("1 exceeded");
    expect(container.textContent).toContain("1 warning");
    expect(container.textContent).toContain("api_calls");
    expect(container.textContent).toContain("50/100");
    expect(container.textContent).toContain("bandwidth");
    expect(container.textContent).toContain("110/100");
  });
});
