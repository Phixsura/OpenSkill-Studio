import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeprecationTrackerTable } from "@/components/deprecation-tracker-table";

describe("DeprecationTrackerTable", () => {
  it("renders deprecations", () => {
    const { container } = render(
      <DeprecationTrackerTable readyToSunset={0} items={[
        { endpoint: "/api/v1/users/search", sunsetDate: "2027-03-01",
          replacement: "/api/v2/users?q=", migrationPct: 75, remaining: 25, readyToSunset: false },
      ]} />
    );
    expect(container.textContent).toContain("Deprecated Endpoints");
    expect(container.textContent).toContain("/api/v1/users/search");
    expect(container.textContent).toContain("/api/v2/users?q=");
    expect(container.textContent).toContain("25 callers remaining");
    expect(container.textContent).toContain("2027-03-01");
  });
});
