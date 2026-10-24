import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FirewallRulesPanel } from "@/components/firewall-rules-panel";

describe("FirewallRulesPanel", () => {
  it("renders rules", () => {
    const { container } = render(
      <FirewallRulesPanel allowCount={1} denyCount={1} onAdd={vi.fn()}
        rules={[
          { name: "allow-http", direction: "ingress", action: "allow", protocol: "tcp", port: 80, source: "0.0.0.0/0" },
          { name: "deny-ssh", direction: "ingress", action: "deny", protocol: "tcp", port: 22, source: "0.0.0.0/0" },
        ]} />
    );
    expect(container.textContent).toContain("Firewall Rules");
    expect(container.textContent).toContain("1 allow");
    expect(container.textContent).toContain("1 deny");
    expect(container.textContent).toContain("TCP:80");
    expect(container.textContent).toContain("TCP:22");
  });
});
