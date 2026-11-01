import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookTransformBuilder } from "@/components/webhook-transform-builder";

const mockPipelines = [
  { id: "p1", name: "Slack Adapter", eventType: "push", enabled: true, executionCount: 42,
    steps: [
      { operation: "filter", config: { include: ["ref", "sha"] } },
      { operation: "map", config: { fields: { ref: "branch" } } },
      { operation: "enrich", config: { fields: { source: "github" } } },
    ]},
  { id: "p2", name: "Disabled", eventType: "deploy", enabled: false, executionCount: 0,
    steps: [{ operation: "wrap", config: { key: "data" } }] },
];

describe("WebhookTransformBuilder", () => {
  it("renders pipelines", () => {
    const { container } = render(<WebhookTransformBuilder pipelines={mockPipelines} />);
    expect(container.textContent).toContain("Slack Adapter");
    expect(container.textContent).toContain("3 steps");
    expect(container.textContent).toContain("×42");
  });

  it("expands to show steps", () => {
    const { getByText, container } = render(<WebhookTransformBuilder pipelines={mockPipelines} />);
    fireEvent.click(getByText("Slack Adapter"));
    expect(container.textContent).toContain("filter");
    expect(container.textContent).toContain("map");
    expect(container.textContent).toContain("enrich");
  });

  it("calls onTest", () => {
    const onTest = vi.fn();
    const { getAllByText } = render(<WebhookTransformBuilder pipelines={mockPipelines} onTest={onTest} />);
    fireEvent.click(getAllByText("Test")[0]);
    expect(onTest).toHaveBeenCalledWith("p1");
  });
});
