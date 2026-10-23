import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RelativeTimeLabel } from "@/components/relative-time-label";

describe("RelativeTimeLabel", () => {
  it("renders", () => {
    const { container } = render(
      <RelativeTimeLabel text="3h ago" fullDate="Oct 23, 2026 12:00 PM" />
    );
    expect(container.textContent).toContain("3h ago");
    expect(container.querySelector("span")?.getAttribute("title")).toContain("Oct 23");
  });
  it("no tooltip", () => {
    const { container } = render(
      <RelativeTimeLabel text="5m ago" fullDate="x" showTooltip={false} />
    );
    expect(container.querySelector("span")?.getAttribute("title")).toBeNull();
  });
});
