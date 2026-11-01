import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { BadgeList } from "@/components/badge-list";

const BADGES = [{ icon: "🔥", label: "Popular", condition: "100+ installs" }, { icon: "⭐", label: "High Quality", condition: "95+" }];

describe("BadgeList", () => {
  it("shows badges", () => {
    const { container } = render(<BadgeList badges={BADGES} />);
    expect(container.textContent).toContain("Popular");
    expect(container.textContent).toContain("🔥");
  });
  it("returns null when empty", () => {
    const { container } = render(<BadgeList badges={[]} />);
    expect(container.innerHTML).toBe("");
  });
});
