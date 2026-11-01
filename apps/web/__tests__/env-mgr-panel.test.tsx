import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EnvMgrPanel } from "@/components/env-mgr-panel";

describe("EnvMgrPanel", () => {
  it("renders", () => {
    const { container } = render(
      <EnvMgrPanel environments={[
        { name: "prod", tier: "premium", region: "us-east", status: "active", services: 5 },
        { name: "staging", tier: "standard", region: "us-east", status: "active", services: 5 },
        { name: "dev", tier: "standard", region: "eu-west", status: "provisioning", services: 2 },
      ]} />
    );
    expect(container.textContent).toContain("Environments");
    expect(container.textContent).toContain("3 environments");
    expect(container.textContent).toContain("prod");
    expect(container.textContent).toContain("premium");
    expect(container.textContent).toContain("staging");
    expect(container.textContent).toContain("5 services");
  });
});
