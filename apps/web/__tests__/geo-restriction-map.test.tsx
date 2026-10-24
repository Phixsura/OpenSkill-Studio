import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { GeoRestrictionMap } from "@/components/geo-restriction-map";

describe("GeoRestrictionMap", () => {
  const countries = [{ code: "US", name: "United States" }, { code: "GB", name: "United Kingdom" }];
  it("renders", () => {
    const { container } = render(
      <GeoRestrictionMap mode="allow" countries={countries} onToggleCountry={vi.fn()} onChangeMode={vi.fn()} />
    );
    expect(container.textContent).toContain("Geo Restrictions");
    expect(container.textContent).toContain("Only available in");
    expect(container.textContent).toContain("US — United States");
  });
  it("toggle country", () => {
    const fn = vi.fn();
    const { container } = render(
      <GeoRestrictionMap mode="block" countries={countries} onToggleCountry={fn} onChangeMode={vi.fn()} />
    );
    const countryBtns = Array.from(container.querySelectorAll("button")).filter(b => b.textContent?.includes("US"));
    fireEvent.click(countryBtns[0]);
    expect(fn).toHaveBeenCalledWith("US");
  });
});
