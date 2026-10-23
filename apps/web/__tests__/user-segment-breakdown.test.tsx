import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UserSegmentBreakdown } from "@/components/user-segment-breakdown";

describe("UserSegmentBreakdown", () => {
  const segments = [
    { name: "established", count: 500, pct: 50 },
    { name: "power_user", count: 200, pct: 20 },
    { name: "new_user", count: 150, pct: 15 },
  ];
  it("renders", () => {
    const { container } = render(<UserSegmentBreakdown totalUsers={1000} segments={segments} />);
    expect(container.textContent).toContain("User Segments");
    expect(container.textContent).toContain("1,000 total");
    expect(container.textContent).toContain("✅ Established");
    expect(container.textContent).toContain("⚡ Power User");
    expect(container.textContent).toContain("500 (50%)");
  });
});
