import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIKeyUsageCard from "../src/components/api-key-usage-card";

const keys = [
  { key_id: "k1", total_requests: 5000, error_rate: 2.5, top_endpoint: "/api/users" },
  { key_id: "k2", total_requests: 1000, error_rate: 10.0, top_endpoint: "/api/apps" },
];

describe("APIKeyUsageCard", () => {
  it("renders header and totals", () => {
    const { container } = render(<APIKeyUsageCard keys={keys} appName="App" />);
    expect(container.textContent).toContain("API Key Usage");
    expect(container.textContent).toContain("6,000 reqs");
  });

  it("shows key IDs and endpoints", () => {
    const { container } = render(<APIKeyUsageCard keys={keys} appName="App" />);
    expect(container.textContent).toContain("k1");
    expect(container.textContent).toContain("/api/users");
  });

  it("shows error rates", () => {
    const { container } = render(<APIKeyUsageCard keys={keys} appName="App" />);
    expect(container.textContent).toContain("2.5% err");
    expect(container.textContent).toContain("10% err");
  });

  it("shows empty state", () => {
    const { container } = render(<APIKeyUsageCard keys={[]} appName="App" />);
    expect(container.textContent).toContain("No API key usage");
  });
});
