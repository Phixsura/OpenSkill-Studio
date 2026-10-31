import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TraceSamplingConfig } from "@/components/trace-sampling-config";

describe("TraceSamplingConfig", () => {
  it("renders rules", () => {
    const onAdd = vi.fn();
    const { container, getByText } = render(
      <TraceSamplingConfig defaultRate={0.1} onAddRule={onAdd} rules={[
        { name: "health", path: "/health", rate: 0.01, rateDisplay: "1%" },
        { name: "api", path: "/api/v1", rate: 0.5, rateDisplay: "50%" },
      ]} />
    );
    expect(container.textContent).toContain("Trace Sampling");
    expect(container.textContent).toContain("Default: 10%");
    expect(container.textContent).toContain("health");
    expect(container.textContent).toContain("1%");
    expect(container.textContent).toContain("50%");
    fireEvent.click(getByText("+ Add Sampling Rule"));
    expect(onAdd).toHaveBeenCalled();
  });
});
