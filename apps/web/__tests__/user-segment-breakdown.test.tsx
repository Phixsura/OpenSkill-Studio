import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UserSegmentBreakdown } from "@/components/user-segment-breakdown";

describe("UserSegmentBreakdown", () => {
  it("renders segments", () => {
    const { container } = render(
      <UserSegmentBreakdown totalUsers={4} summary={{
        power_users: { count: 1, pct: 25 },
        new_users: { count: 1, pct: 25 },
        churning: { count: 1, pct: 25 },
        unclassified: { count: 1, pct: 25 },
      }} />
    );
    expect(container.textContent).toContain("User Segments");
    expect(container.textContent).toContain("4");
    expect(container.textContent).toContain("Power Users");
    expect(container.textContent).toContain("Churning");
    expect(container.textContent).toContain("25%");
  });
});
