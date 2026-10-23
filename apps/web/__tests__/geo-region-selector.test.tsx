import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { GeoRegionSelector } from "@/components/geo-region-selector";

describe("GeoRegionSelector", () => {
  const regions = [
    { id: "us-east-1", name: "US East", flag: "🇺🇸", continent: "North America", latency_ms: 20 },
    { id: "eu-west-1", name: "EU West", flag: "🇮🇪", continent: "Europe", latency_ms: 80 },
  ];
  it("renders grouped regions", () => {
    const { container } = render(
      <GeoRegionSelector regions={regions} selected="us-east-1" recommended="us-east-1" onSelect={vi.fn()} />
    );
    expect(container.textContent).toContain("US East");
    expect(container.textContent).toContain("EU West");
    expect(container.textContent).toContain("Recommended");
    expect(container.textContent).toContain("20ms");
  });
  it("calls onSelect", () => {
    const fn = vi.fn();
    const { container } = render(
      <GeoRegionSelector regions={regions} selected="" recommended="us-east-1" onSelect={fn} />
    );
    fireEvent.click(container.querySelectorAll("button")[1]);
    expect(fn).toHaveBeenCalledWith("eu-west-1");
  });
});
