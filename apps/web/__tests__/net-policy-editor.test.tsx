import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NetPolicyEditor } from "@/components/net-policy-editor";

describe("NetPolicyEditor", () => {
  it("renders rules", () => {
    const { container } = render(
      <NetPolicyEditor onAdd={vi.fn()} onDelete={vi.fn()} rules={[
        { name: "allow-http", direction: "ingress", action: "allow", source: "*", destination: "10.0.0.1", port: 80, protocol: "tcp" },
        { name: "deny-ssh", direction: "ingress", action: "deny", source: "*", destination: "*", port: 22, protocol: "tcp" },
      ]} />
    );
    expect(container.textContent).toContain("Network Policies");
    expect(container.textContent).toContain("2 rules");
    expect(container.textContent).toContain("allow");
    expect(container.textContent).toContain("deny");
    expect(container.textContent).toContain("TCP:80");
    expect(container.textContent).toContain("TCP:22");
  });
});
