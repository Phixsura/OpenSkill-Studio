import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIUsageQuotaCard from "../src/components/api-usage-quota-card";

const quotas = [
  { metric: "api_calls", used: 8000, limit: 10000, pct: 80 },
  { metric: "storage_mb", used: 600, limit: 500, pct: 120 },
];

describe("APIUsageQuotaCard", () => {
  it("renders header with period", () => {
    const { container } = render(
      <APIUsageQuotaCard quotas={quotas} period="2024-01" appName="App" />,
    );
    expect(container.textContent).toContain("Usage Quotas");
    expect(container.textContent).toContain("2024-01");
  });

  it("shows overage count", () => {
    const { container } = render(
      <APIUsageQuotaCard quotas={quotas} period="2024-01" appName="App" />,
    );
    expect(container.textContent).toContain("1 over limit");
  });

  it("shows metrics with usage", () => {
    const { container } = render(
      <APIUsageQuotaCard quotas={quotas} period="2024-01" appName="App" />,
    );
    expect(container.textContent).toContain("api_calls");
    expect(container.textContent).toContain("8,000");
  });

  it("shows empty state", () => {
    const { container } = render(<APIUsageQuotaCard quotas={[]} period="2024-01" appName="App" />);
    expect(container.textContent).toContain("No usage quotas");
  });
});
