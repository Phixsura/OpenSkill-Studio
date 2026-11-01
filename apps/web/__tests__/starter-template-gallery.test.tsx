import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { StarterTemplateGallery } from "@/components/starter-template-gallery";

const mockTemplates = [
  { id: "t1", name: "Slack Bot", description: "Build a Slack integration",
    category: "integration", runtime: "node20", tags: ["slack", "bot"],
    popularity: 100, variableCount: 2 },
  { id: "t2", name: "Data Pipeline", description: "ETL data pipeline",
    category: "data_sync", runtime: "python3.12", tags: ["etl", "data"],
    popularity: 50, variableCount: 3 },
];

describe("StarterTemplateGallery", () => {
  it("renders templates", () => {
    const { container } = render(<StarterTemplateGallery templates={mockTemplates} />);
    expect(container.textContent).toContain("Slack Bot");
    expect(container.textContent).toContain("Data Pipeline");
  });

  it("filters by search", () => {
    const { container } = render(<StarterTemplateGallery templates={mockTemplates} />);
    const input = container.querySelector("input");
    if (input) fireEvent.change(input, { target: { value: "slack" } });
    expect(container.textContent).toContain("Slack Bot");
    expect(container.textContent).not.toContain("Data Pipeline");
  });

  it("calls onUse", () => {
    const onUse = vi.fn();
    const { getAllByText } = render(<StarterTemplateGallery templates={mockTemplates} onUse={onUse} />);
    fireEvent.click(getAllByText("Use")[0]);
    expect(onUse).toHaveBeenCalledWith("t1");
  });

  it("filters by category", () => {
    const { getByText, container } = render(<StarterTemplateGallery templates={mockTemplates} />);
    fireEvent.click(getByText("🔄 data_sync"));
    expect(container.textContent).toContain("Data Pipeline");
    expect(container.textContent).not.toContain("Slack Bot");
  });
});
