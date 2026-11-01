import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ConfigSchemaPanel } from "@/components/config-schema-panel";

const mockFields = [
  { name: "theme", type: "string", required: true, enum: ["light", "dark"] },
  { name: "max_items", type: "integer", required: true, default: 50 },
  { name: "debug", type: "boolean" },
];
const mockVersions = [
  { version: 1, fieldCount: 2, schemaId: "cs_abc" },
  { version: 2, fieldCount: 3, schemaId: "cs_def" },
];

describe("ConfigSchemaPanel", () => {
  it("renders fields with types", () => {
    const { container } = render(
      <ConfigSchemaPanel fields={mockFields} versions={mockVersions} validationResult={null} />
    );
    expect(container.textContent).toContain("theme");
    expect(container.textContent).toContain("string");
    expect(container.textContent).toContain("required");
    expect(container.textContent).toContain("[light, dark]");
  });

  it("shows validation result", () => {
    const result = { valid: false, errors: ["Missing required: theme"], defaultsApplied: {}, schemaVersion: 2 };
    const { container } = render(
      <ConfigSchemaPanel fields={mockFields} versions={mockVersions} validationResult={result} />
    );
    expect(container.textContent).toContain("Invalid");
    expect(container.textContent).toContain("Missing required: theme");
  });

  it("shows versions tab", () => {
    const onSelect = vi.fn();
    const { getByText } = render(
      <ConfigSchemaPanel fields={mockFields} versions={mockVersions} validationResult={null} onSelectVersion={onSelect} />
    );
    fireEvent.click(getByText("Versions (2)"));
    fireEvent.click(getByText("v1"));
    expect(onSelect).toHaveBeenCalledWith(1);
  });

  it("calls onValidate", () => {
    const onValidate = vi.fn();
    const { getByText } = render(
      <ConfigSchemaPanel fields={mockFields} versions={[]} validationResult={null} onValidate={onValidate} />
    );
    fireEvent.click(getByText("Validate"));
    expect(onValidate).toHaveBeenCalled();
  });
});
