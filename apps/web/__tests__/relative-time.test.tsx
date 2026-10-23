import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RelativeTime } from "@/components/relative-time";

describe("RelativeTime", () => {
  it("renders relative time", () => {
    const { container } = render(<RelativeTime relative="5m ago" absolute="2026-01-01 10:00 UTC" />);
    expect(container.textContent).toContain("5m ago");
    expect(container.querySelector("time")?.getAttribute("title")).toBe("2026-01-01 10:00 UTC");
  });
});
