import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIKeyDashboardCard from "../src/components/api-developer-api-key-dashboard-card";

const dash = { total_keys: 50, active_keys: 40, expired_keys: 8, revoked_keys: 2, total_requests_today: 5000, keys_expiring_soon: 3 };

describe("APIDeveloperAPIKeyDashboardCard", () => {
  it("shows all metrics", () => {
    const { container } = render(<APIDeveloperAPIKeyDashboardCard dashboard={dash} appName="App" />);
    expect(container.textContent).toContain("API Key Dashboard");
    expect(container.textContent).toContain("40");
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("3");
  });
});
