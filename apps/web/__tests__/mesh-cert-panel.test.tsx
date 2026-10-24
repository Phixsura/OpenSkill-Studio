import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MeshCertPanel } from "@/components/mesh-cert-panel";
describe("MeshCertPanel", () => {
  it("renders", () => {
    const { container } = render(
      <MeshCertPanel active={2} revoked={1}
        certs={[
          { service: "api", fingerprint: "abc123def456", status: "active", validityDays: 365 },
          { service: "db", fingerprint: "xyz789", status: "revoked", validityDays: 0 },
        ]} />
    );
    expect(container.textContent).toContain("Mesh Certificates");
    expect(container.textContent).toContain("2 active");
    expect(container.textContent).toContain("1 revoked");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("abc123def456");
  });
});
