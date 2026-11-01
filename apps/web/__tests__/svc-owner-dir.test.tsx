import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SvcOwnerDir } from "@/components/svc-owner-dir";

describe("SvcOwnerDir", () => {
  it("renders", () => {
    const { container } = render(
      <SvcOwnerDir teamCount={2}
        services={[
          { service: "auth", team: "platform", oncall: "alice", escalation: ["alice", "bob"] },
          { service: "billing", team: "finance", oncall: "carol", escalation: ["carol"] },
        ]} />
    );
    expect(container.textContent).toContain("Service Owners");
    expect(container.textContent).toContain("2 services");
    expect(container.textContent).toContain("2 teams");
    expect(container.textContent).toContain("auth");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("alice → bob");
  });
});
