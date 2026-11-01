import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-ip-allowlist-card";

describe("ConsumerApiIpAllowlistCard", () => {
  it("shows entries", () => {
    const entries = [{ id: "e1", cidr: "10.0.0.0/24", label: "Office", addedAt: "2026-06-01" }];
    const { container } = render(<Card entries={entries} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("IP Allowlist");
    expect(container.textContent).toContain("10.0.0.0/24");
    expect(container.textContent).toContain("Office");
  });
  it("shows no restrictions", () => {
    const { container } = render(<Card entries={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No IP restrictions");
  });
});
