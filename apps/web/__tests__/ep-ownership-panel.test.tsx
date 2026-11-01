import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EpOwnershipPanel } from "@/components/ep-ownership-panel";
describe("EpOwnershipPanel", () => {
  it("renders", () => {
    const { container } = render(
      <EpOwnershipPanel teams={2} unownedCount={1}
        endpoints={[
          { endpoint: "/api/users", team: "user-team", oncall: "alice", tier: "critical" },
          { endpoint: "/api/orders", team: "order-team", oncall: "bob", tier: "standard" },
        ]} />
    );
    expect(container.textContent).toContain("Endpoint Ownership");
    expect(container.textContent).toContain("2 owned");
    expect(container.textContent).toContain("2 teams");
    expect(container.textContent).toContain("1 unowned");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("user-team");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("[critical]");
  });
});
