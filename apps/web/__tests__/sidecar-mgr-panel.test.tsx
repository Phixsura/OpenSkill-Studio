import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SidecarMgrPanel } from "@/components/sidecar-mgr-panel";

describe("SidecarMgrPanel", () => {
  it("renders", () => {
    const { container } = render(
      <SidecarMgrPanel mtlsEnabled={2}
        sidecars={[
          { service: "api", proxy: "envoy", mtls: true, port: 15001 },
          { service: "worker", proxy: "envoy", mtls: true, port: 15001 },
          { service: "legacy", proxy: "envoy", mtls: false, port: 15001 },
        ]} />
    );
    expect(container.textContent).toContain("Sidecar Proxies");
    expect(container.textContent).toContain("3 injected");
    expect(container.textContent).toContain("2 mTLS");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("mTLS");
    expect(container.textContent).toContain("plain");
  });
});
