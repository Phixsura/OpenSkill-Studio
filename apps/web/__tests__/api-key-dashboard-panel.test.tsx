import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiKeyDashboardPanel } from "@/components/api-key-dashboard-panel";

const overview = { total: 10, active: 7, expired: 2, revoked: 1, expiringSoon: 2, unused: 1, totalUsage: 50000 };
const alerts = [{ key: "prod-key", alert: "Expiring in <3 days", severity: "high" }];

describe("ApiKeyDashboardPanel", () => {
  it("renders overview and alerts", () => {
    const { container } = render(<ApiKeyDashboardPanel overview={overview} alerts={alerts} />);
    expect(container.textContent).toContain("7");
    expect(container.textContent).toContain("50,000");
    expect(container.textContent).toContain("prod-key");
    expect(container.textContent).toContain("Expiring");
  });
});
