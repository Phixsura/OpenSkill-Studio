import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import NetworkPolicyCard from "../src/components/network-policy-card";

const rules = [
  {
    rule_id: "r1",
    direction: "egress" as const,
    action: "allow" as const,
    destination: "api.stripe.com",
    port: 443,
    protocol: "https",
  },
  {
    rule_id: "r2",
    direction: "egress" as const,
    action: "deny" as const,
    destination: "evil.com",
    port: null,
    protocol: "any",
  },
];

describe("NetworkPolicyCard", () => {
  it("renders header", () => {
    const { container } = render(<NetworkPolicyCard rules={rules} appName="My App" />);
    expect(container.textContent).toContain("Network Policy");
  });

  it("shows rule and deny counts", () => {
    const { container } = render(<NetworkPolicyCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("2 rules");
    expect(container.textContent).toContain("1 deny");
  });

  it("renders destinations", () => {
    const { container } = render(<NetworkPolicyCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("api.stripe.com");
    expect(container.textContent).toContain("evil.com");
  });

  it("shows port info", () => {
    const { container } = render(<NetworkPolicyCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("port 443");
    expect(container.textContent).toContain("any port");
  });

  it("shows allow/deny icons", () => {
    const { container } = render(<NetworkPolicyCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("✓");
    expect(container.textContent).toContain("✕");
  });

  it("shows empty state", () => {
    const { container } = render(<NetworkPolicyCard rules={[]} appName="App" />);
    expect(container.textContent).toContain("No network rules");
  });
});
