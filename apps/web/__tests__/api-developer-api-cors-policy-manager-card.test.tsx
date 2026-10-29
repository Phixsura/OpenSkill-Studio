import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPICORSPolicyManagerCard from "../src/components/api-developer-api-cors-policy-manager-card";

const policies = [
  { policy_id: "main", allowed_origins: ["https://app.com"], allowed_methods: ["GET", "POST"], allow_credentials: true, max_age_seconds: 3600 },
];

describe("APIDeveloperAPICORSPolicyManagerCard", () => {
  it("shows policies", () => {
    const { container } = render(<APIDeveloperAPICORSPolicyManagerCard policies={policies} appName="App" />);
    expect(container.textContent).toContain("CORS Policies");
    expect(container.textContent).toContain("main");
    expect(container.textContent).toContain("https://app.com");
    expect(container.textContent).toContain("credentials");
    expect(container.textContent).toContain("GET, POST");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPICORSPolicyManagerCard policies={[]} appName="App" />);
    expect(container.textContent).toContain("No CORS policies");
  });
});
