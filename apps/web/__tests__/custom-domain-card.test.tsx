import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import CustomDomainCard from "../src/components/custom-domain-card";

const domains = [
  {
    domain_id: "d1",
    hostname: "api.example.com",
    target: "app-123.internal",
    dns_status: "verified" as const,
    ssl_status: "active" as const,
    is_ready: true,
  },
  {
    domain_id: "d2",
    hostname: "docs.example.com",
    target: "app-456.internal",
    dns_status: "pending" as const,
    ssl_status: "none" as const,
    is_ready: false,
  },
];

describe("CustomDomainCard", () => {
  it("renders header and ready count", () => {
    const { container } = render(<CustomDomainCard domains={domains} appName="App" />);
    expect(container.textContent).toContain("Custom Domains");
    expect(container.textContent).toContain("1/2 ready");
  });

  it("shows hostnames", () => {
    const { container } = render(<CustomDomainCard domains={domains} appName="App" />);
    expect(container.textContent).toContain("api.example.com");
    expect(container.textContent).toContain("docs.example.com");
  });

  it("shows DNS status", () => {
    const { container } = render(<CustomDomainCard domains={domains} appName="App" />);
    expect(container.textContent).toContain("DNS verified");
    expect(container.textContent).toContain("DNS pending");
  });

  it("shows SSL status and target", () => {
    const { container } = render(<CustomDomainCard domains={domains} appName="App" />);
    expect(container.textContent).toContain("SSL active");
    expect(container.textContent).toContain("app-123.internal");
  });

  it("shows empty state", () => {
    const { container } = render(<CustomDomainCard domains={[]} appName="App" />);
    expect(container.textContent).toContain("No custom domains");
  });
});
