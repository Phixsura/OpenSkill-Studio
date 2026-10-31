import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { QuotaUsagePanel } from "@/components/quota-usage-panel";

const mockQuotas = [
  { resource: "api_calls", state: "ok" as const, current: 500, softLimit: 800, hardLimit: 1000, usagePercent: 50 },
  { resource: "storage_mb", state: "warning" as const, current: 85, softLimit: 80, hardLimit: 100, usagePercent: 85 },
  { resource: "bandwidth_mb", state: "exceeded" as const, current: 105, softLimit: 80, hardLimit: 100, usagePercent: 105 },
];

describe("QuotaUsagePanel", () => {
  it("renders quotas with usage", () => {
    const { container } = render(
      <QuotaUsagePanel quotas={mockQuotas} extensionName="MyExt" />
    );
    expect(container.textContent).toContain("api calls");
    expect(container.textContent).toContain("500 / 1000");
    expect(container.textContent).toContain("2 issues");
  });

  it("shows state colors", () => {
    const { container } = render(
      <QuotaUsagePanel quotas={mockQuotas} extensionName="Test" />
    );
    expect(container.textContent).toContain("ok");
    expect(container.textContent).toContain("warning");
    expect(container.textContent).toContain("exceeded");
  });

  it("shows soft/hard limit markers", () => {
    const { container } = render(
      <QuotaUsagePanel quotas={mockQuotas} extensionName="Test" />
    );
    expect(container.textContent).toContain("soft: 800");
    expect(container.textContent).toContain("hard: 1000");
  });

  it("calls onReset for non-ok quotas", () => {
    const onReset = vi.fn();
    const { getAllByText } = render(
      <QuotaUsagePanel quotas={mockQuotas} extensionName="Test" onReset={onReset} />
    );
    fireEvent.click(getAllByText("Reset")[0]);
    expect(onReset).toHaveBeenCalledWith("storage_mb");
  });
});
