import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIOAuthClientCard from "../src/components/api-oauth-client-card";

const clients = [
  { client_id: "oc_abc123def456ghi", client_name: "Mobile App", grant_types: ["authorization_code", "refresh_token"], redirect_uri_count: 2, active: true },
  { client_id: "oc_xyz789uvw012qrs", client_name: "Service Bot", grant_types: ["client_credentials"], redirect_uri_count: 1, active: false },
];

describe("APIOAuthClientCard", () => {
  it("renders header and active count", () => {
    const { container } = render(<APIOAuthClientCard clients={clients} appName="App" />);
    expect(container.textContent).toContain("OAuth Clients");
    expect(container.textContent).toContain("1/2 active");
  });

  it("shows client names and grant types", () => {
    const { container } = render(<APIOAuthClientCard clients={clients} appName="App" />);
    expect(container.textContent).toContain("Mobile App");
    expect(container.textContent).toContain("authorization_code");
    expect(container.textContent).toContain("client_credentials");
  });

  it("shows empty state", () => {
    const { container } = render(<APIOAuthClientCard clients={[]} appName="App" />);
    expect(container.textContent).toContain("No OAuth clients");
  });
});
