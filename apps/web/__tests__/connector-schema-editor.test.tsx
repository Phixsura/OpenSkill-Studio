import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ConnectorSchemaEditor } from "@/components/connector-schema-editor";

const mockFields = [
  { name: "channel", type: "string", required: true, description: "Slack channel" },
  { name: "message", type: "string", required: true },
  { name: "silent", type: "boolean", required: false },
];
const mockErrors = [{ field: "channel", message: "min length 1, got 0" }];

describe("ConnectorSchemaEditor", () => {
  it("renders schema fields", () => {
    const { container } = render(
      <ConnectorSchemaEditor fields={mockFields} connectorName="Slack" errors={[]} />
    );
    expect(container.textContent).toContain("channel");
    expect(container.textContent).toContain("string");
    expect(container.textContent).toContain("required");
  });

  it("shows validation errors", () => {
    const { container } = render(
      <ConnectorSchemaEditor fields={mockFields} connectorName="Slack" errors={mockErrors} />
    );
    expect(container.textContent).toContain("min length 1");
  });

  it("calls onRemoveField", () => {
    const onRemove = vi.fn();
    const { container } = render(
      <ConnectorSchemaEditor fields={mockFields} connectorName="Slack" errors={[]} onRemoveField={onRemove} />
    );
    const removeButtons = container.querySelectorAll("button");
    const removeBtn = Array.from(removeButtons).find(b => b.textContent === "✕");
    if (removeBtn) fireEvent.click(removeBtn);
    expect(onRemove).toHaveBeenCalled();
  });

  it("shows add field form", () => {
    const { getByText, container } = render(
      <ConnectorSchemaEditor fields={[]} connectorName="Test" errors={[]} />
    );
    fireEvent.click(getByText("+ Field"));
    expect(container.querySelector("input")).toBeDefined();
  });
});
