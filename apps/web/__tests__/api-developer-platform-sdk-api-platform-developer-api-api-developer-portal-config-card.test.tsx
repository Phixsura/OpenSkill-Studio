import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-developer-portal-config-card";

describe("DeveloperPortalConfigCard", () => {
  it("shows portals", () => {
    const portals = [{ portal_id: "p1", title: "My API", primary_color: "#3B82F6", sections: ["docs", "sdks"], custom_domain: "api.example.com", signup_enabled: true }];
    const { container } = render(<Card portals={portals} appName="App" />);
    expect(container.textContent).toContain("Developer Portal");
    expect(container.textContent).toContain("My API");
    expect(container.textContent).toContain("docs");
    expect(container.textContent).toContain("signups on");
  });
  it("shows empty", () => {
    const { container } = render(<Card portals={[]} appName="App" />);
    expect(container.textContent).toContain("No portals configured");
  });
});
