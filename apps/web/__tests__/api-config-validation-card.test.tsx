import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIConfigValidationCard from "../src/components/api-config-validation-card";

const rules = [
  { key: "db_host", rule_type: "required", value: "" },
  { key: "env", rule_type: "enum", value: "prod,staging" },
];
const errors = ["Missing required key: db_host"];

describe("APIConfigValidationCard", () => {
  it("renders header and error count", () => {
    const { container } = render(<APIConfigValidationCard rules={rules} errors={errors} appName="App" />);
    expect(container.textContent).toContain("Config Validation");
    expect(container.textContent).toContain("1 errors");
  });

  it("shows errors and rules", () => {
    const { container } = render(<APIConfigValidationCard rules={rules} errors={errors} appName="App" />);
    expect(container.textContent).toContain("Missing required key");
    expect(container.textContent).toContain("db_host");
    expect(container.textContent).toContain("enum: prod,staging");
  });

  it("shows clean state", () => {
    const { container } = render(<APIConfigValidationCard rules={rules} errors={[]} appName="App" />);
    expect(container.textContent).not.toContain("errors");
  });
});
