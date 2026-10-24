import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ResourceLimitsEditor } from "@/components/resource-limits-editor";

describe("ResourceLimitsEditor", () => {
  it("shows current memory", () => {
    const { container } = render(<ResourceLimitsEditor memoryMb={256} timeoutSeconds={30} onChange={vi.fn()} />);
    expect(container.textContent).toContain("256 MB");
  });

  it("shows current timeout", () => {
    const { container } = render(<ResourceLimitsEditor memoryMb={128} timeoutSeconds={60} onChange={vi.fn()} />);
    expect(container.textContent).toContain("60s");
  });

  it("has range inputs", () => {
    const { container } = render(<ResourceLimitsEditor memoryMb={128} timeoutSeconds={30} onChange={vi.fn()} />);
    expect(container.querySelectorAll("input[type='range']").length).toBe(2);
  });

  it("shows max values", () => {
    const { container } = render(<ResourceLimitsEditor memoryMb={128} timeoutSeconds={30} maxMemory={1024} maxTimeout={300} onChange={vi.fn()} />);
    expect(container.textContent).toContain("1024 MB");
    expect(container.textContent).toContain("300s");
  });
});
