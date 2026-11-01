import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ConfigTemplatePanel } from "@/components/config-template-panel";

const mockTemplate = {
  id: "db", name: "Database Config",
  variables: [
    { name: "db_host", varType: "string", required: true, default: "localhost" },
    { name: "db_port", varType: "string", required: false, default: "5432" },
  ],
};

describe("ConfigTemplatePanel", () => {
  it("renders template form", () => {
    const { container } = render(<ConfigTemplatePanel template={mockTemplate} renderedConfig={null} />);
    expect(container.textContent).toContain("Database Config");
    expect(container.textContent).toContain("db_host");
  });

  it("shows rendered config", () => {
    const { container } = render(
      <ConfigTemplatePanel template={mockTemplate} renderedConfig={{ host: "localhost:5432" }} />
    );
    expect(container.textContent).toContain("localhost:5432");
  });

  it("calls onRender", () => {
    const onRender = vi.fn();
    const { getByText } = render(<ConfigTemplatePanel template={mockTemplate} renderedConfig={null} onRender={onRender} />);
    fireEvent.click(getByText("Render Config"));
    expect(onRender).toHaveBeenCalled();
  });
});
