import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-custom-domain-card";

describe("CustomDomainCard", () => {
  it("shows domains", () => {
    const domains = [{ domain_id: "d1", domain: "api.example.com", status: "active", ssl_enabled: true, consumer_id: "c1" }];
    const { container } = render(<Card domains={domains} appName="App" />);
    expect(container.textContent).toContain("Custom Domains");
    expect(container.textContent).toContain("api.example.com");
    expect(container.textContent).toContain("active");
  });
  it("shows empty", () => {
    const { container } = render(<Card domains={[]} appName="App" />);
    expect(container.textContent).toContain("No custom domains");
  });
});
