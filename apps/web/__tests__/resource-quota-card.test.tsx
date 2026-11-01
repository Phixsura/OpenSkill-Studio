import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ResourceQuotaCard from "../src/components/resource-quota-card";

const quotas = [
  { resource: "storage_gb", used: 75, limit: 100, usage_pct: 75, exceeded: false },
  { resource: "api_calls", used: 9500, limit: 10000, usage_pct: 95, exceeded: false },
  { resource: "webhooks", used: 50, limit: 50, usage_pct: 100, exceeded: true },
];

describe("ResourceQuotaCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<ResourceQuotaCard quotas={quotas} appName="My App" />);
    expect(container.textContent).toContain("Resource Quotas");
    expect(container.textContent).toContain("My App");
  });

  it("shows exceeded badge", () => {
    const { container } = render(<ResourceQuotaCard quotas={quotas} appName="App" />);
    expect(container.textContent).toContain("1 exceeded");
  });

  it("shows within-limits when all ok", () => {
    const okQuotas = quotas.filter((q) => !q.exceeded);
    const { container } = render(<ResourceQuotaCard quotas={okQuotas} appName="App" />);
    expect(container.textContent).toContain("Within limits");
  });

  it("renders resource names with spaces", () => {
    const { container } = render(<ResourceQuotaCard quotas={quotas} appName="App" />);
    expect(container.textContent).toContain("storage gb");
    expect(container.textContent).toContain("api calls");
  });

  it("shows used/limit values", () => {
    const { container } = render(<ResourceQuotaCard quotas={quotas} appName="App" />);
    expect(container.textContent).toContain("75 / 100");
    expect(container.textContent).toContain("9.5K / 10.0K");
  });

  it("shows empty state", () => {
    const { container } = render(<ResourceQuotaCard quotas={[]} appName="App" />);
    expect(container.textContent).toContain("No quotas configured");
  });
});
