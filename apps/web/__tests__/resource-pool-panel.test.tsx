import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ResourcePoolPanel } from "@/components/resource-pool-panel";

const mockPools = [
  { resource: "cpu", total: 8, allocated: 5, reserved: 1, available: 2, utilizationPct: 62.5, queued: 0 },
  { resource: "memory", total: 32, allocated: 28, reserved: 0, available: 4, utilizationPct: 87.5, queued: 2 },
  { resource: "gpu", total: 4, allocated: 4, reserved: 0, available: 0, utilizationPct: 100, queued: 3 },
];

describe("ResourcePoolPanel", () => {
  it("renders pool resources", () => {
    const { container } = render(<ResourcePoolPanel pools={mockPools} />);
    expect(container.textContent).toContain("cpu");
    expect(container.textContent).toContain("memory");
    expect(container.textContent).toContain("gpu");
  });

  it("shows utilization percentages", () => {
    const { container } = render(<ResourcePoolPanel pools={mockPools} />);
    expect(container.textContent).toContain("62.5%");
    expect(container.textContent).toContain("87.5%");
    expect(container.textContent).toContain("100%");
  });

  it("shows queued count", () => {
    const { container } = render(<ResourcePoolPanel pools={mockPools} />);
    expect(container.textContent).toContain("2 queued");
    expect(container.textContent).toContain("3 queued");
  });

  it("shows allocation details", () => {
    const { container } = render(<ResourcePoolPanel pools={mockPools} />);
    expect(container.textContent).toContain("5/8 cores");
    expect(container.textContent).toContain("Reserved: 1");
    expect(container.textContent).toContain("Available: 2");
  });
});
