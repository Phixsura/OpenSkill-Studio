import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ResourceConfig } from "@/components/resource-config";

describe("ResourceConfig", () => {
  const presets = [
    { id: "small", cpuM: 250, memoryMb: 256, replicas: 1, monthlyCostUsd: 5 },
    { id: "medium", cpuM: 500, memoryMb: 512, replicas: 2, monthlyCostUsd: 20 },
  ];
  it("renders presets", () => {
    const { container } = render(<ResourceConfig presets={presets} selected="small" onSelect={vi.fn()} />);
    expect(container.textContent).toContain("small");
    expect(container.textContent).toContain("medium");
    expect(container.textContent).toContain("$5/mo");
  });
  it("select preset", () => {
    const fn = vi.fn();
    const { container } = render(<ResourceConfig presets={presets} selected="" onSelect={fn} />);
    fireEvent.click(container.querySelectorAll("button")[1]);
    expect(fn).toHaveBeenCalledWith("medium");
  });
});
