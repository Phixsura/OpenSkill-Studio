import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiCustomDomainManagerCard from "../src/components/api-developer-platform-sdk-api-developer-api-custom-domain-manager-card";

const domains = [
  { domain: "api.example.com", status: "active", ssl_status: "provisioned" },
  { domain: "dev.example.com", status: "pending", ssl_status: "pending" },
];

describe("Card", () => {
  it("shows domains", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiCustomDomainManagerCard domains={domains} appName="App" />);
    expect(container.textContent).toContain("Custom Domains");
    expect(container.textContent).toContain("1/2 active");
    expect(container.textContent).toContain("api.example.com");
    expect(container.textContent).toContain("active");
    expect(container.textContent).toContain("pending");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiCustomDomainManagerCard domains={[]} appName="App" />);
    expect(container.textContent).toContain("No custom domains");
  });
});
