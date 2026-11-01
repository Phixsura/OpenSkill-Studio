import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ResourceQuotaDashboard } from "@/components/resource-quota-dashboard";

describe("ResourceQuotaDashboard", () => {
  it("renders quotas", () => {
    const { container } = render(
      <ResourceQuotaDashboard plan="pro" quotas={{
        api_calls: { limit: 50000, unlimited: false, usage: 12000, pctUsed: 24 },
        storage_mb: { limit: 5000, unlimited: false, usage: 3500, pctUsed: 70 },
      }} />
    );
    expect(container.textContent).toContain("Resource Quotas");
    expect(container.textContent).toContain("pro");
    expect(container.textContent).toContain("api calls");
    expect(container.textContent).toContain("storage mb");
  });
});
