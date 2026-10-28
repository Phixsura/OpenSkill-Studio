import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import IPAllowListCard from "../src/components/ip-allowlist-card";

const rules = [
  { rule_id: "r1", network: "10.0.0.0/8", description: "Internal network" },
  { rule_id: "r2", network: "203.0.113.50/32", description: "Office IP" },
];

describe("IPAllowListCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <IPAllowListCard rules={rules} mode="allowlist" appName="My App" />,
    );
    expect(container.textContent).toContain("IP Access Control");
    expect(container.textContent).toContain("My App");
  });

  it("shows allowlist mode badge", () => {
    const { container } = render(<IPAllowListCard rules={rules} mode="allowlist" appName="App" />);
    expect(container.textContent).toContain("Allowlist");
  });

  it("shows denylist mode badge", () => {
    const { container } = render(<IPAllowListCard rules={rules} mode="denylist" appName="App" />);
    expect(container.textContent).toContain("Denylist");
  });

  it("shows rule count", () => {
    const { container } = render(<IPAllowListCard rules={rules} mode="allowlist" appName="App" />);
    expect(container.textContent).toContain("2 rules");
  });

  it("renders networks", () => {
    const { container } = render(<IPAllowListCard rules={rules} mode="allowlist" appName="App" />);
    expect(container.textContent).toContain("10.0.0.0/8");
    expect(container.textContent).toContain("203.0.113.50/32");
  });

  it("shows descriptions", () => {
    const { container } = render(<IPAllowListCard rules={rules} mode="allowlist" appName="App" />);
    expect(container.textContent).toContain("Internal network");
    expect(container.textContent).toContain("Office IP");
  });

  it("shows empty allowlist message", () => {
    const { container } = render(<IPAllowListCard rules={[]} mode="allowlist" appName="App" />);
    expect(container.textContent).toContain("all IPs allowed");
  });

  it("shows empty denylist message", () => {
    const { container } = render(<IPAllowListCard rules={[]} mode="denylist" appName="App" />);
    expect(container.textContent).toContain("no IPs blocked");
  });
});
