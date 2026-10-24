import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeprecationManager } from "@/components/deprecation-manager";

describe("DeprecationManager", () => {
  it("renders deprecated", () => {
    const { container } = render(
      <DeprecationManager totalCalls={500} actionNeeded={true}
        endpoints={[
          { path: "/v1/users", method: "GET", sunsetDate: "2025-06-01", replacement: "/v2/users", recentCalls: 500 },
        ]} />
    );
    expect(container.textContent).toContain("Deprecated APIs");
    expect(container.textContent).toContain("1 deprecated");
    expect(container.textContent).toContain("500 calls");
    expect(container.textContent).toContain("/v1/users");
    expect(container.textContent).toContain("2025-06-01");
    expect(container.textContent).toContain("/v2/users");
  });
});
