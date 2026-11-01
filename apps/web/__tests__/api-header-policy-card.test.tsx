import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIHeaderPolicyCard from "../src/components/api-header-policy-card";

const rules = [
  { rule_id: "r1", header_name: "X-Request-Id", action: "require" as const, value: "" },
  { rule_id: "r2", header_name: "Server", action: "forbid" as const, value: "" },
  { rule_id: "r3", header_name: "X-Frame-Options", action: "set_default" as const, value: "DENY" },
];

describe("APIHeaderPolicyCard", () => {
  it("renders header and rule count", () => {
    const { container } = render(<APIHeaderPolicyCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("Header Policy");
    expect(container.textContent).toContain("3 rules");
  });

  it("shows action badges and header names", () => {
    const { container } = render(<APIHeaderPolicyCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("require");
    expect(container.textContent).toContain("X-Request-Id");
    expect(container.textContent).toContain("forbid");
    expect(container.textContent).toContain("set default");
  });

  it("shows default values", () => {
    const { container } = render(<APIHeaderPolicyCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("DENY");
  });

  it("shows empty state", () => {
    const { container } = render(<APIHeaderPolicyCard rules={[]} appName="App" />);
    expect(container.textContent).toContain("No header rules");
  });
});
