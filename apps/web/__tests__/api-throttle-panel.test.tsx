import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiThrottlePanel } from "@/components/api-throttle-panel";

describe("ApiThrottlePanel", () => {
  it("renders", () => {
    const { container } = render(
      <ApiThrottlePanel totalTenants={2}
        tenants={[
          { tenantId: "t1", used: 95, limit: 100, pctUsed: 95 },
          { tenantId: "t2", used: 30, limit: 100, pctUsed: 30 },
        ]} />
    );
    expect(container.textContent).toContain("API Throttle");
    expect(container.textContent).toContain("2 tenants");
    expect(container.textContent).toContain("t1");
    expect(container.textContent).toContain("95/100");
    expect(container.textContent).toContain("t2");
    expect(container.textContent).toContain("30/100");
  });
});
