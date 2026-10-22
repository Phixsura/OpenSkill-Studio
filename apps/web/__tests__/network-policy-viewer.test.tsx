import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { NetworkPolicyViewer } from "@/components/network-policy-viewer";

describe("NetworkPolicyViewer", () => {
  it("renders policy", () => {
    const { container } = render(
      <NetworkPolicyViewer allowedHosts={["api.example.com"]} blockedPorts={[22, 5432]} maxConnections={50} bandwidthLimitMbps={10} />
    );
    expect(container.textContent).toContain("api.example.com");
    expect(container.textContent).toContain("22, 5432");
    expect(container.textContent).toContain("50");
    expect(container.textContent).toContain("10 Mbps");
  });
  it("shows empty hosts", () => {
    const { container } = render(
      <NetworkPolicyViewer allowedHosts={[]} blockedPorts={[]} maxConnections={10} bandwidthLimitMbps={5} />
    );
    expect(container.textContent).toContain("None configured");
  });
});
