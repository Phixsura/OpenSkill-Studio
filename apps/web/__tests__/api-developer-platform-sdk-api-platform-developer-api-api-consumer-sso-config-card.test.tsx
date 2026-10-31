import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-sso-config-card";

describe("SsoConfigCard", () => {
  it("shows SSO configs", () => {
    const configs = [{ config_id: "s1", consumer_id: "c1", provider: "oidc", enabled: true, enforce: true, domains: ["corp.com"] }];
    const { container } = render(<Card configs={configs} appName="App" />);
    expect(container.textContent).toContain("SSO Config");
    expect(container.textContent).toContain("c1");
    expect(container.textContent).toContain("enforced");
    expect(container.textContent).toContain("corp.com");
  });
  it("shows empty", () => {
    const { container } = render(<Card configs={[]} appName="App" />);
    expect(container.textContent).toContain("No SSO configured");
  });
});
