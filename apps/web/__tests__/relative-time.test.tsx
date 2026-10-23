import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RelativeTime } from "@/components/relative-time";

describe("RelativeTime", () => {
  it("renders old date", () => {
    const { container } = render(<RelativeTime date="2020-01-01T00:00:00Z" />);
    expect(container.textContent).toContain("y ago");
  });
  it("has time element", () => {
    const { container } = render(<RelativeTime date="2026-01-01T00:00:00Z" />);
    const time = container.querySelector("time");
    expect(time).toBeTruthy();
    expect(time?.getAttribute("dateTime")).toBe("2026-01-01T00:00:00Z");
  });
});
