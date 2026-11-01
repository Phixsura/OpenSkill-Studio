import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DataMapperPanel } from "@/components/data-mapper-panel";

const mockMappings = [
  { id: "m1", name: "Slack to Jira", sourceConnector: "Slack", targetConnector: "Jira",
    fieldMappings: [
      { sourceField: "channel", targetField: "project", transform: "rename" },
      { sourceField: "user.name", targetField: "reporter", transform: "extract" },
      { sourceField: "priority", targetField: "urgency", transform: "cast" },
    ]},
];

describe("DataMapperPanel", () => {
  it("renders mappings", () => {
    const { container } = render(<DataMapperPanel mappings={mockMappings} />);
    expect(container.textContent).toContain("Slack to Jira");
    expect(container.textContent).toContain("3 fields");
  });

  it("expands to show field mappings", () => {
    const { container } = render(<DataMapperPanel mappings={mockMappings} />);
    const row = container.querySelector("[class*='cursor-pointer']");
    if (row) fireEvent.click(row);
    expect(container.textContent).toContain("channel");
    expect(container.textContent).toContain("reporter");
    expect(container.textContent).toContain("extract");
  });

  it("calls onTest", () => {
    const onTest = vi.fn();
    const { getByText } = render(<DataMapperPanel mappings={mockMappings} onTest={onTest} />);
    fireEvent.click(getByText("Test"));
    expect(onTest).toHaveBeenCalledWith("m1");
  });
});
