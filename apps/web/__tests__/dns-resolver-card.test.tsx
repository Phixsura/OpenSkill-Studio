import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import DNSResolverCard from "../src/components/dns-resolver-card";

const records = [
  {
    hostname: "api.example.com",
    addresses: ["10.0.0.1", "10.0.0.2"],
    ttl_seconds: 300,
    lookup_ms: 12,
    failed: false,
    error: "",
  },
  {
    hostname: "bad.example.com",
    addresses: [],
    ttl_seconds: 60,
    lookup_ms: 0,
    failed: true,
    error: "NXDOMAIN",
  },
];

describe("DNSResolverCard", () => {
  it("renders header", () => {
    const { container } = render(<DNSResolverCard records={records} appName="My App" />);
    expect(container.textContent).toContain("DNS Resolver");
  });

  it("shows cached and failed counts", () => {
    const { container } = render(<DNSResolverCard records={records} appName="App" />);
    expect(container.textContent).toContain("2 cached");
    expect(container.textContent).toContain("1 failed");
  });

  it("renders hostnames and addresses", () => {
    const { container } = render(<DNSResolverCard records={records} appName="App" />);
    expect(container.textContent).toContain("api.example.com");
    expect(container.textContent).toContain("10.0.0.1, 10.0.0.2");
  });

  it("shows error for failed", () => {
    const { container } = render(<DNSResolverCard records={records} appName="App" />);
    expect(container.textContent).toContain("NXDOMAIN");
  });

  it("shows lookup time and TTL", () => {
    const { container } = render(<DNSResolverCard records={records} appName="App" />);
    expect(container.textContent).toContain("12ms");
    expect(container.textContent).toContain("TTL 300s");
  });

  it("shows empty state", () => {
    const { container } = render(<DNSResolverCard records={[]} appName="App" />);
    expect(container.textContent).toContain("No DNS records cached");
  });
});
