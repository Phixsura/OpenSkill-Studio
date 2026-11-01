import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-request-validation-rule-card";

describe("ValidationRuleCard", () => {
  it("shows rules", () => {
    const rules = [{ rule_id: "r1", field_name: "email", rule_type: "regex" }];
    const { container } = render(<Card endpoint="/api/users" rules={rules} totalRules={5} appName="App" />);
    expect(container.textContent).toContain("Validation Rules");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("email");
    expect(container.textContent).toContain("5 total rules");
  });
  it("shows empty", () => {
    const { container } = render(<Card endpoint="/api" rules={[]} totalRules={0} appName="App" />);
    expect(container.textContent).toContain("No validation rules");
  });
});
