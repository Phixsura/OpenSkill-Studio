import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import RequestValidatorCard from "../src/components/request-validator-card";

const rules = [
  { rule_id: "r1", rule_type: "required_header", value: "Authorization", enabled: true },
  { rule_id: "r2", rule_type: "content_type", value: "application/json", enabled: true },
  { rule_id: "r3", rule_type: "max_size", value: "1048576", enabled: false },
];

describe("RequestValidatorCard", () => {
  it("renders header and active count", () => {
    const { container } = render(<RequestValidatorCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("Request Validator");
    expect(container.textContent).toContain("2/3 active");
  });

  it("shows rule type labels", () => {
    const { container } = render(<RequestValidatorCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("Header");
    expect(container.textContent).toContain("Content-Type");
    expect(container.textContent).toContain("Max Size");
  });

  it("shows rule values", () => {
    const { container } = render(<RequestValidatorCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("Authorization");
    expect(container.textContent).toContain("application/json");
  });

  it("shows empty state", () => {
    const { container } = render(<RequestValidatorCard rules={[]} appName="App" />);
    expect(container.textContent).toContain("No validation rules");
  });
});
