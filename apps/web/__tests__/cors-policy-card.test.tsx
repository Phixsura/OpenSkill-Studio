import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import CORSPolicyCard from "../src/components/cors-policy-card";

const policies = [
  {
    policy_id: "p1",
    allowed_origins: ["https://app.example.com"],
    allowed_methods: ["GET", "POST"],
    allowed_headers: ["Content-Type"],
    allow_credentials: true,
    max_age_seconds: 3600,
  },
  {
    policy_id: "p2",
    allowed_origins: ["*"],
    allowed_methods: ["GET"],
    allowed_headers: ["Content-Type"],
    allow_credentials: false,
    max_age_seconds: 600,
  },
];

describe("CORSPolicyCard", () => {
  it("renders header and count", () => {
    const { container } = render(<CORSPolicyCard policies={policies} appName="App" />);
    expect(container.textContent).toContain("CORS Policies");
    expect(container.textContent).toContain("2 policies");
  });

  it("shows origin info", () => {
    const { container } = render(<CORSPolicyCard policies={policies} appName="App" />);
    expect(container.textContent).toContain("1 origins");
    expect(container.textContent).toContain("All origins (*)");
  });

  it("shows methods", () => {
    const { container } = render(<CORSPolicyCard policies={policies} appName="App" />);
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("POST");
  });

  it("shows credentials badge", () => {
    const { container } = render(<CORSPolicyCard policies={policies} appName="App" />);
    expect(container.textContent).toContain("credentials");
  });

  it("shows empty state", () => {
    const { container } = render(<CORSPolicyCard policies={[]} appName="App" />);
    expect(container.textContent).toContain("No CORS policies");
  });
});
