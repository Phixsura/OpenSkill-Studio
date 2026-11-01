import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { NetworkPolicyViewer } from "@/components/network-policy-viewer";

describe("NetworkPolicyViewer", () => {
  it("renders policies", () => {
    const { container } = render(
      <NetworkPolicyViewer totalRules={5} policies={[
        { name: "api-policy", target: "api", ingressCount: 2, egressCount: 1, enabled: true },
        { name: "db-policy", target: "database", ingressCount: 3, egressCount: 0, enabled: false },
      ]} />
    );
    expect(container.textContent).toContain("Network Policies");
    expect(container.textContent).toContain("2 policies");
    expect(container.textContent).toContain("5 rules");
    expect(container.textContent).toContain("api-policy");
    expect(container.textContent).toContain("2 ingress");
    expect(container.textContent).toContain("1 egress");
  });
});
