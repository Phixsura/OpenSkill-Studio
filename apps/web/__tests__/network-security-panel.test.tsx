import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { NetworkSecurityPanel } from "@/components/network-security-panel";

describe("NetworkSecurityPanel", () => {
  it("renders panel", () => {
    const { container } = render(
      <NetworkSecurityPanel allowedDomains={["api.example.com"]} blockedRequests={5} totalRequests={500} mode="allowlist" />
    );
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("5");
    expect(container.textContent).toContain("api.example.com");
    expect(container.textContent).toContain("allowlist");
  });
});
