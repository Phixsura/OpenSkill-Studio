import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DiscoveryCarousel } from "@/components/discovery-carousel";

describe("DiscoveryCarousel", () => {
  const recs = [{ id: "a3", name: "Dev IDE", icon: "💻", category: "tools", rating: 4.8, reason: "Based on interests" }];
  it("renders recommendations", () => {
    const { container } = render(
      <DiscoveryCarousel recommendations={recs} basedOn={["code", "tools"]} onSelect={vi.fn()} />
    );
    expect(container.textContent).toContain("Recommended for You");
    expect(container.textContent).toContain("Dev IDE");
    expect(container.textContent).toContain("code, tools");
  });
  it("hides when empty", () => {
    const { container } = render(
      <DiscoveryCarousel recommendations={[]} basedOn={[]} onSelect={vi.fn()} />
    );
    expect(container.innerHTML).toBe("");
  });
});
