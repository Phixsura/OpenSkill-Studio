import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { NetworkPolicyView } from "@/components/network-policy-view";

describe("NetworkPolicyView", () => {
  const ingress = [{ source: "0.0.0.0/0", protocol: "tcp", port: 443, action: "allow", description: "" }];
  const egress = [{ source: "10.0.0.0/8", protocol: "tcp", port: 5432, action: "allow", description: "DB" }];
  it("renders rules", () => {
    const { container } = render(<NetworkPolicyView ingress={ingress} egress={egress} />);
    expect(container.textContent).toContain("Network Policy");
    expect(container.textContent).toContain("Ingress");
    expect(container.textContent).toContain("Egress");
    expect(container.textContent).toContain("TCP:443");
    expect(container.textContent).toContain("allow");
  });
});
