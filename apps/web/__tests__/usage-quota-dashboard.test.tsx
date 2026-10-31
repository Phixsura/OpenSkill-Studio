import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UsageQuotaDashboard } from "@/components/usage-quota-dashboard";

describe("UsageQuotaDashboard", () => {
  it("shows empty state", () => {
    const { container } = render(<UsageQuotaDashboard quotas={[]} />);
    expect(container.textContent).toContain("No quotas configured");
  });
  it("renders quotas with warning", () => {
    const quotas = [
      { resource: "API Calls", used: 950, limit: 1000, unit: "calls" },
      { resource: "Storage", used: 200, limit: 500, unit: "MB" },
    ];
    const { container } = render(<UsageQuotaDashboard quotas={quotas} />);
    expect(container.textContent).toContain("API Calls");
    expect(container.textContent).toContain("Approaching limit");
    expect(container.textContent).toContain("Storage");
  });
});
