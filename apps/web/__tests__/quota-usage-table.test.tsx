import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { QuotaUsageTable } from "@/components/quota-usage-table";

const ITEMS = [
  { resource: "apps", used: 8, limit: 10, pct: 80, warning: true, exceeded: false },
  { resource: "api_keys", used: 5, limit: 5, pct: 100, warning: true, exceeded: true },
];

describe("QuotaUsageTable", () => {
  it("shows resources", () => {
    const { container } = render(<QuotaUsageTable items={ITEMS} />);
    expect(container.textContent).toContain("apps");
    expect(container.textContent).toContain("api keys");
  });
  it("shows usage", () => {
    const { container } = render(<QuotaUsageTable items={ITEMS} />);
    expect(container.textContent).toContain("8/10");
    expect(container.textContent).toContain("5/5");
  });
});
