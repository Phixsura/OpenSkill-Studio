import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { QuotaUsagePanel } from "@/components/quota-usage-panel";

describe("QuotaUsagePanel", () => {
  it("renders quotas", () => {
    const { container } = render(
      <QuotaUsagePanel quotas={[
        { resource: "api_calls", usage: 85, hard: 100, soft: 80, pct: 85, unit: "count", status: "warning" },
        { resource: "storage", usage: 500, hard: 1000, soft: 800, pct: 50, unit: "MB", status: "ok" },
      ]} />
    );
    expect(container.textContent).toContain("Quotas");
    expect(container.textContent).toContain("api calls");
    expect(container.textContent).toContain("85");
    expect(container.textContent).toContain("/ 100");
    expect(container.textContent).toContain("storage");
    expect(container.textContent).toContain("500");
  });
});
