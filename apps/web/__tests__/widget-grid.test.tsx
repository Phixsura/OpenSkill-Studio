import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WidgetGrid } from "@/components/widget-grid";

describe("WidgetGrid", () => {
  it("renders widgets", () => {
    const onRemove = vi.fn();
    const { container, getAllByText } = render(
      <WidgetGrid onRemove={onRemove} widgets={[
        { id: "api_calls", title: "API Calls", icon: "📡", size: "sm", type: "metric" },
        { id: "deploy_status", title: "Deploy Status", icon: "🚀", size: "md", type: "status" },
      ]} />
    );
    expect(container.textContent).toContain("API Calls");
    expect(container.textContent).toContain("Deploy Status");
    expect(container.textContent).toContain("metric widget");
    fireEvent.click(getAllByText("×")[0]);
    expect(onRemove).toHaveBeenCalledWith("api_calls");
  });
});
