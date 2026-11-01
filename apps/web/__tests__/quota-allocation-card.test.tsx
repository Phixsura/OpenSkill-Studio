import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import QuotaAllocationCard from "../src/components/quota-allocation-card";

const quotas = [
  { resource: "api_calls", limit: 10000, used: 8500, unit: "requests" },
  { resource: "storage", limit: 500, used: 200, unit: "MB" },
  { resource: "bandwidth", limit: 100, used: 95, unit: "GB" },
];

describe("QuotaAllocationCard", () => {
  it("renders header and count", () => {
    const { container } = render(<QuotaAllocationCard quotas={quotas} appName="My App" />);
    expect(container.textContent).toContain("Quota Allocation");
    expect(container.textContent).toContain("3 quotas");
  });

  it("shows resource names", () => {
    const { container } = render(<QuotaAllocationCard quotas={quotas} appName="App" />);
    expect(container.textContent).toContain("api_calls");
    expect(container.textContent).toContain("storage");
    expect(container.textContent).toContain("bandwidth");
  });

  it("shows usage with units", () => {
    const { container } = render(<QuotaAllocationCard quotas={quotas} appName="App" />);
    expect(container.textContent).toContain("requests");
    expect(container.textContent).toContain("MB");
  });

  it("shows percentages", () => {
    const { container } = render(<QuotaAllocationCard quotas={quotas} appName="App" />);
    expect(container.textContent).toContain("85%");
    expect(container.textContent).toContain("40%");
    expect(container.textContent).toContain("95%");
  });

  it("shows empty state", () => {
    const { container } = render(<QuotaAllocationCard quotas={[]} appName="App" />);
    expect(container.textContent).toContain("No quotas configured");
  });
});
