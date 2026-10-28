import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import CustomDomainCard from "../src/components/custom-domain-card";

const domains = [
  {
    domain_id: "d1",
    domain: "app.example.com",
    status: "verified" as const,
    ssl_status: "active" as const,
  },
  {
    domain_id: "d2",
    domain: "api.example.com",
    status: "verifying" as const,
    ssl_status: "provisioning" as const,
  },
  {
    domain_id: "d3",
    domain: "beta.example.com",
    status: "failed" as const,
    ssl_status: "none" as const,
  },
];

describe("CustomDomainCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<CustomDomainCard domains={domains} appName="My App" />);
    expect(container.textContent).toContain("Custom Domains");
    expect(container.textContent).toContain("My App");
  });

  it("shows verified count", () => {
    const { container } = render(<CustomDomainCard domains={domains} appName="App" />);
    expect(container.textContent).toContain("1/3 verified");
  });

  it("renders domain names", () => {
    const { container } = render(<CustomDomainCard domains={domains} appName="App" />);
    expect(container.textContent).toContain("app.example.com");
    expect(container.textContent).toContain("api.example.com");
  });

  it("shows SSL status", () => {
    const { container } = render(<CustomDomainCard domains={domains} appName="App" />);
    expect(container.textContent).toContain("SSL active");
    expect(container.textContent).toContain("SSL provisioning");
    expect(container.textContent).toContain("No SSL");
  });

  it("shows verification status", () => {
    const { container } = render(<CustomDomainCard domains={domains} appName="App" />);
    expect(container.textContent).toContain("verified");
    expect(container.textContent).toContain("verifying");
    expect(container.textContent).toContain("failed");
  });

  it("shows empty state", () => {
    const { container } = render(<CustomDomainCard domains={[]} appName="App" />);
    expect(container.textContent).toContain("No custom domains");
  });
});
