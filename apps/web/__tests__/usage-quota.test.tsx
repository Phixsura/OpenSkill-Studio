import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UsageQuota } from "@/components/usage-quota";

describe("UsageQuota", () => {
  const resources = [
    { name: "API Calls", used: 8500, limit: 10000, pct: 85, status: "warning", unit: "calls/mo" },
    { name: "Storage", used: 2, limit: 10, pct: 20, status: "ok", unit: "GB" },
    { name: "Bandwidth", used: 95, limit: 100, pct: 95, status: "critical", unit: "GB" },
  ];
  it("renders resources", () => {
    const { container } = render(<UsageQuota resources={resources} />);
    expect(container.textContent).toContain("API Calls");
    expect(container.textContent).toContain("Storage");
    expect(container.textContent).toContain("Bandwidth");
    expect(container.textContent).toContain("Approaching limit");
  });
});
