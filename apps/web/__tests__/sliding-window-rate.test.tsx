import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SlidingWindowRate } from "@/components/sliding-window-rate";

describe("SlidingWindowRate", () => {
  it("renders rates", () => {
    const { container } = render(
      <SlidingWindowRate keys={[
        { key: "user1", count: 45, limit: 100, remaining: 55, allowed: true },
        { key: "user2", count: 98, limit: 100, remaining: 2, allowed: true },
      ]} />
    );
    expect(container.textContent).toContain("Sliding Window Rates");
    expect(container.textContent).toContain("2 tracked");
    expect(container.textContent).toContain("user1");
    expect(container.textContent).toContain("45/100");
    expect(container.textContent).toContain("user2");
    expect(container.textContent).toContain("2 left");
  });
});
