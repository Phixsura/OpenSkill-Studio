import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-oauth-client-card";

describe("ConsumerOauthClientCard", () => {
  it("shows clients", () => {
    const clients = [{ clientId: "app1", name: "My App", redirectUris: ["https://x.com/cb"], scopes: ["read", "write"], active: true, createdAt: "2026-06-01" }];
    const { container } = render(<Card clients={clients} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("OAuth Clients");
    expect(container.textContent).toContain("My App");
    expect(container.textContent).toContain("app1");
    expect(container.textContent).toContain("Active");
    expect(container.textContent).toContain("read");
  });
  it("shows empty", () => {
    const { container } = render(<Card clients={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No OAuth clients");
  });
});
