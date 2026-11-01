import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ResponseTransformCard from "../src/components/response-transform-card";

const rules = [
  { rule_id: "r1", action: "rename" as const, field: "user_name", value: "username" },
  { rule_id: "r2", action: "remove" as const, field: "internal_id", value: "" },
  { rule_id: "r3", action: "default" as const, field: "status", value: "active" },
];

describe("ResponseTransformCard", () => {
  it("renders header and count", () => {
    const { container } = render(<ResponseTransformCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("Response Transform");
    expect(container.textContent).toContain("3 rules");
  });

  it("shows action badges", () => {
    const { container } = render(<ResponseTransformCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("rename");
    expect(container.textContent).toContain("remove");
    expect(container.textContent).toContain("default");
  });

  it("shows fields and values", () => {
    const { container } = render(<ResponseTransformCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("user_name");
    expect(container.textContent).toContain("→ username");
  });

  it("shows empty state", () => {
    const { container } = render(<ResponseTransformCard rules={[]} appName="App" />);
    expect(container.textContent).toContain("No transform rules");
  });
});
