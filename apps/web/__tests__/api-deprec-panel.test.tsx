import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiDeprecPanel } from "@/components/api-deprec-panel";
describe("ApiDeprecPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ApiDeprecPanel readyCount={0}
        endpoints={[
          { endpoint: "/api/v1/users", sunsetDate: "2027-01-01", replacement: "/api/v2/users",
            migrationPct: 50, readyToSunset: false },
        ]} />
    );
    expect(container.textContent).toContain("API Deprecations");
    expect(container.textContent).toContain("1 deprecated");
    expect(container.textContent).toContain("/api/v1/users");
    expect(container.textContent).toContain("50% migrated");
    expect(container.textContent).toContain("/api/v2/users");
    expect(container.textContent).toContain("2027-01-01");
  });
});
