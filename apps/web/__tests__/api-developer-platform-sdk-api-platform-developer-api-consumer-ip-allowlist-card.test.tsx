import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-consumer-ip-allowlist-card";

describe("IpAllowlistCard", () => {
  it("shows entries", () => {
    const entries = [{ entry_id: "e1", network: "10.0.0.0/24", label: "Office" }];
    const { container } = render(<Card consumerId="c1" entries={entries} appName="App" />);
    expect(container.textContent).toContain("IP Allowlist");
    expect(container.textContent).toContain("10.0.0.0/24");
    expect(container.textContent).toContain("Office");
  });
  it("shows no restrictions", () => {
    const { container } = render(<Card consumerId="c1" entries={[]} appName="App" />);
    expect(container.textContent).toContain("No IP restrictions");
  });
});
