import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { InputValidatorPanel } from "@/components/input-validator-panel";

const mockRules = [
  { field: "name", rule: "required" },
  { field: "age", rule: "type", value: "integer" },
  { field: "email", rule: "pattern", value: ".+@.+" },
];
const mockErrors = [
  { field: "name", message: "name is required", rule: "required" },
  { field: "age", message: "age must be integer", rule: "type" },
];

describe("InputValidatorPanel", () => {
  it("renders rules", () => {
    const { container } = render(
      <InputValidatorPanel rules={mockRules} errors={[]} isValid={null} xssDetected={false} />
    );
    expect(container.textContent).toContain("name");
    expect(container.textContent).toContain("required");
    expect(container.textContent).toContain("Rules (3)");
  });

  it("shows validation result", () => {
    const { container } = render(
      <InputValidatorPanel rules={[]} errors={mockErrors} isValid={false} xssDetected={true} />
    );
    expect(container.textContent).toContain("Invalid");
    expect(container.textContent).toContain("XSS");
  });

  it("shows errors tab", () => {
    const { getByText, container } = render(
      <InputValidatorPanel rules={mockRules} errors={mockErrors} isValid={false} xssDetected={false} />
    );
    fireEvent.click(getByText("Errors (2)"));
    expect(container.textContent).toContain("name is required");
    expect(container.textContent).toContain("age must be integer");
  });

  it("calls onValidate and onSanitize", () => {
    const onValidate = vi.fn();
    const onSanitize = vi.fn();
    const { getByText } = render(
      <InputValidatorPanel rules={[]} errors={[]} isValid={null} xssDetected={false}
        onValidate={onValidate} onSanitize={onSanitize} />
    );
    fireEvent.click(getByText("Validate"));
    expect(onValidate).toHaveBeenCalled();
    fireEvent.click(getByText("Sanitize"));
    expect(onSanitize).toHaveBeenCalled();
  });
});
