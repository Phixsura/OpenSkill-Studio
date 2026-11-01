import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DataValidatorPanel } from "@/components/data-validator-panel";

const mockSchema = [
  { name: "name", type: "string", required: true, hasNested: false },
  { name: "age", type: "integer", required: true, hasNested: false },
  { name: "address", type: "object", required: false, hasNested: true },
];
const mockErrors = [
  { path: "name", message: "Required field missing" },
  { path: "address.city", message: "Expected string" },
];

describe("DataValidatorPanel", () => {
  it("renders schema fields", () => {
    const { container } = render(
      <DataValidatorPanel schema={mockSchema} errors={[]} isValid={null} />
    );
    expect(container.textContent).toContain("name");
    expect(container.textContent).toContain("string");
    expect(container.textContent).toContain("required");
    expect(container.textContent).toContain("nested");
  });

  it("shows validation result", () => {
    const { container } = render(
      <DataValidatorPanel schema={mockSchema} errors={mockErrors} isValid={false} />
    );
    expect(container.textContent).toContain("2 errors");
  });

  it("shows error paths", () => {
    const { getByText, container } = render(
      <DataValidatorPanel schema={mockSchema} errors={mockErrors} isValid={false} />
    );
    fireEvent.click(getByText("Errors (2)"));
    expect(container.textContent).toContain("address.city");
    expect(container.textContent).toContain("Expected string");
  });

  it("calls onValidate", () => {
    const onValidate = vi.fn();
    const { getByText } = render(
      <DataValidatorPanel schema={mockSchema} errors={[]} isValid={null} onValidate={onValidate} />
    );
    fireEvent.click(getByText("Validate"));
    expect(onValidate).toHaveBeenCalled();
  });
});
