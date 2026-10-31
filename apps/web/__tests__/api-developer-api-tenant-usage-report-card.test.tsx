import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPITenantUsageReportCard from "../src/components/api-developer-api-tenant-usage-report-card";

const tenants = [
  { tenant_id: "acme-corp", api_calls: 50000, webhook_deliveries: 10000, storage_bytes: 536870912, total_cost_cents: 150 },
];

describe("APIDeveloperAPITenantUsageReportCard", () => {
  it("shows tenant usage", () => {
    const { container } = render(<APIDeveloperAPITenantUsageReportCard tenants={tenants} totalCostCents={150} appName="App" />);
    expect(container.textContent).toContain("Tenant Usage Report");
    expect(container.textContent).toContain("acme-corp");
    expect(container.textContent).toContain("50,000 calls");
    expect(container.textContent).toContain("$1.50");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPITenantUsageReportCard tenants={[]} totalCostCents={0} appName="App" />);
    expect(container.textContent).toContain("No tenant data");
  });
});
