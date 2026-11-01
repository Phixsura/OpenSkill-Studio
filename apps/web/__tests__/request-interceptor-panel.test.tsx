import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RequestInterceptorPanel } from "@/components/request-interceptor-panel";

const mockInterceptors = [
  { interceptorId: "i1", name: "Auth Header", phase: "before" as const, action: "modify" as const,
    enabled: true, executionCount: 100, order: 0 },
  { interceptorId: "i2", name: "Block External", phase: "before" as const, action: "block" as const,
    enabled: true, executionCount: 5, order: 1 },
  { interceptorId: "i3", name: "Cache GET", phase: "after" as const, action: "cache" as const,
    enabled: false, executionCount: 50, order: 0 },
];

describe("RequestInterceptorPanel", () => {
  it("renders interceptors grouped by phase", () => {
    const { container } = render(<RequestInterceptorPanel interceptors={mockInterceptors} />);
    expect(container.textContent).toContain("Auth Header");
    expect(container.textContent).toContain("Before Request");
    expect(container.textContent).toContain("After Response");
  });

  it("shows action badges", () => {
    const { container } = render(<RequestInterceptorPanel interceptors={mockInterceptors} />);
    expect(container.textContent).toContain("modify");
    expect(container.textContent).toContain("block");
    expect(container.textContent).toContain("cache");
  });

  it("calls onToggle", () => {
    const onToggle = vi.fn();
    const { getAllByText } = render(
      <RequestInterceptorPanel interceptors={mockInterceptors} onToggle={onToggle} />
    );
    fireEvent.click(getAllByText("Off")[0]);
    expect(onToggle).toHaveBeenCalledWith("i3");
  });

  it("shows execution count", () => {
    const { container } = render(<RequestInterceptorPanel interceptors={mockInterceptors} />);
    expect(container.textContent).toContain("×100");
  });
});
