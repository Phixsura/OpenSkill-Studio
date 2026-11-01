import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-cors-policy-card";

describe("CorsPolicyCard", () => {
  it("shows policies", () => {
    const policies = [{ policy_id: "p1", endpoint: "/api", origins: ["https://example.com"], credentials: true, max_age_s: 86400 }];
    const { container } = render(<Card policies={policies} appName="App" />);
    expect(container.textContent).toContain("CORS Policies");
    expect(container.textContent).toContain("/api");
    expect(container.textContent).toContain("https://example.com");
    expect(container.textContent).toContain("credentials");
  });
  it("shows empty", () => {
    const { container } = render(<Card policies={[]} appName="App" />);
    expect(container.textContent).toContain("No CORS policies");
  });
});
