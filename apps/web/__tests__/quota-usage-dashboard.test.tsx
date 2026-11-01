import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { QuotaUsageDashboard } from "@/components/quota-usage-dashboard";

const MOCK_POOLS = [
  {
    org_id: "org-1",
    quota_type: "requests",
    total: 10000,
    reserved: 7000,
    used: 4500,
    available: 3000,
    utilization_pct: 45.0,
    allocations: [
      {
        alloc_id: "a1",
        entity_id: "app-crm",
        entity_type: "app",
        reserved: 5000,
        used: 3500,
        usage_pct: 70,
      },
      {
        alloc_id: "a2",
        entity_id: "app-lms",
        entity_type: "app",
        reserved: 2000,
        used: 1000,
        usage_pct: 50,
      },
    ],
  },
  {
    org_id: "org-1",
    quota_type: "storage_mb",
    total: 5120,
    reserved: 4096,
    used: 3800,
    available: 1024,
    utilization_pct: 74.2,
    allocations: [
      {
        alloc_id: "a3",
        entity_id: "app-crm",
        entity_type: "app",
        reserved: 4096,
        used: 3800,
        usage_pct: 92.8,
      },
    ],
  },
];

describe("QuotaUsageDashboard", () => {
  it("renders heading and org name", () => {
    const { container } = render(<QuotaUsageDashboard pools={MOCK_POOLS} orgName="Acme Corp" />);
    expect(container.textContent).toContain("Quota Usage");
    expect(container.textContent).toContain("Acme Corp");
  });

  it("renders pool count", () => {
    const { container } = render(<QuotaUsageDashboard pools={MOCK_POOLS} orgName="Acme" />);
    expect(container.textContent).toContain("2 quota pools");
  });

  it("renders overall utilization", () => {
    const { container } = render(<QuotaUsageDashboard pools={MOCK_POOLS} orgName="Acme" />);
    expect(container.textContent).toContain("overall utilization");
  });

  it("renders quota type labels", () => {
    const { container } = render(<QuotaUsageDashboard pools={MOCK_POOLS} orgName="Acme" />);
    expect(container.textContent).toContain("API Requests");
    expect(container.textContent).toContain("Storage");
  });

  it("renders used and total values", () => {
    const { container } = render(<QuotaUsageDashboard pools={MOCK_POOLS} orgName="Acme" />);
    expect(container.textContent).toContain("4.5K used");
    expect(container.textContent).toContain("10.0K total");
  });

  it("renders allocation entity names", () => {
    const { container } = render(<QuotaUsageDashboard pools={MOCK_POOLS} orgName="Acme" />);
    expect(container.textContent).toContain("app-crm");
    expect(container.textContent).toContain("app-lms");
  });

  it("renders utilization percentages", () => {
    const { container } = render(<QuotaUsageDashboard pools={MOCK_POOLS} orgName="Acme" />);
    expect(container.textContent).toContain("45.0%");
    expect(container.textContent).toContain("74.2%");
  });

  it("shows empty state", () => {
    const { container } = render(<QuotaUsageDashboard pools={[]} orgName="Acme" />);
    expect(container.textContent).toContain("No quota pools configured");
  });

  it("renders reserved and available", () => {
    const { container } = render(<QuotaUsageDashboard pools={MOCK_POOLS} orgName="Acme" />);
    expect(container.textContent).toContain("reserved");
    expect(container.textContent).toContain("available");
  });

  it("renders icons for quota types", () => {
    const { container } = render(<QuotaUsageDashboard pools={MOCK_POOLS} orgName="Acme" />);
    expect(container.textContent).toContain("📡");
    expect(container.textContent).toContain("💾");
  });
});
