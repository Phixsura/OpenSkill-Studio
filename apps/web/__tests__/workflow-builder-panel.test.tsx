import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WorkflowBuilderPanel } from "@/components/workflow-builder-panel";

describe("WorkflowBuilderPanel", () => {
  it("renders form elements", () => {
    const { container, getByPlaceholderText, getByText } = render(
      <WorkflowBuilderPanel />
    );
    expect(getByPlaceholderText("My Automation...")).toBeDefined();
    expect(getByText("⚙️ Workflow Builder")).toBeDefined();
    expect(getByText("🔔 Event")).toBeDefined();
    expect(getByText("+ Add Step")).toBeDefined();
    expect(getByText("💾 Save Workflow")).toBeDefined();
  });

  it("adds and removes steps", () => {
    const { getByText, getAllByText } = render(<WorkflowBuilderPanel />);
    fireEvent.click(getByText("+ Add Step"));
    fireEvent.click(getByText("+ Add Step"));
    const removeButtons = getAllByText("✕");
    expect(removeButtons.length).toBe(3);
    fireEvent.click(removeButtons[2]);
    expect(getAllByText("✕").length).toBe(2);
  });

  it("selects trigger type", () => {
    const { getByText } = render(<WorkflowBuilderPanel />);
    const webhookBtn = getByText("🌐 Webhook");
    fireEvent.click(webhookBtn);
    expect(webhookBtn.className).toContain("bg-blue-600");
  });
});
