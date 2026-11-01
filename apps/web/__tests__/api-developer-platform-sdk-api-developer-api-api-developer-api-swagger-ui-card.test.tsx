import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiApiDeveloperApiSwaggerUICard from "../src/components/api-developer-platform-sdk-api-developer-api-api-developer-api-swagger-ui-card";

describe("Card", () => {
  it("shows config", () => {
    const config = { title: "My API", version: "2.0", base_url: "https://api.example.com", auth_type: "bearer", theme: "dark", try_it_enabled: true, page_views: 5000 };
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiDeveloperApiSwaggerUICard config={config} appName="App" />);
    expect(container.textContent).toContain("Swagger UI");
    expect(container.textContent).toContain("My API v2.0");
    expect(container.textContent).toContain("bearer");
    expect(container.textContent).toContain("5,000 views");
  });
  it("shows not configured", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiDeveloperApiSwaggerUICard config={null} appName="App" />);
    expect(container.textContent).toContain("Not configured");
  });
});
