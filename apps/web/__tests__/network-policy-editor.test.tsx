import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NetworkPolicyEditor } from "@/components/network-policy-editor";

describe("NetworkPolicyEditor", () => {
  const rules = [
    { direction: "egress", target: "api.stripe.com", port: 443, protocol: "tcp", action: "allow" },
    { direction: "ingress", target: "*", port: 8080, protocol: "tcp", action: "allow" },
  ];
  it("renders", () => {
    const { container } = render(<NetworkPolicyEditor rules={rules} onAdd={vi.fn()} onRemove={vi.fn()} />);
    expect(container.textContent).toContain("Network Policy");
    expect(container.textContent).toContain("Egress");
    expect(container.textContent).toContain("api.stripe.com");
    expect(container.textContent).toContain("ALLOW");
    expect(container.textContent).toContain("Ingress");
  });
});
