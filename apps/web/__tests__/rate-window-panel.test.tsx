import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RateWindowPanel } from "@/components/rate-window-panel";

const mockEndpoints = [
  { endpoint: "/api/data", current: 25, limit: 100, burst: 10, windowSeconds: 60, usagePercent: 25 },
  { endpoint: "/api/search", current: 85, limit: 100, burst: 0, windowSeconds: 60, usagePercent: 85 },
  { endpoint: "/api/write", current: 98, limit: 100, burst: 5, windowSeconds: 60, usagePercent: 98 },
];

describe("RateWindowPanel", () => {
  it("renders endpoints with usage", () => {
    const { container } = render(<RateWindowPanel endpoints={mockEndpoints} />);
    expect(container.textContent).toContain("/api/data");
    expect(container.textContent).toContain("25/100 requests");
    expect(container.textContent).toContain("25%");
  });

  it("shows burst allowance", () => {
    const { container } = render(<RateWindowPanel endpoints={mockEndpoints} />);
    expect(container.textContent).toContain("+10 burst");
  });

  it("shows high usage color", () => {
    const { container } = render(<RateWindowPanel endpoints={mockEndpoints} />);
    expect(container.textContent).toContain("98%");
  });

  it("calls onReset", () => {
    const onReset = vi.fn();
    const { getAllByText } = render(<RateWindowPanel endpoints={mockEndpoints} onReset={onReset} />);
    fireEvent.click(getAllByText("Reset")[0]);
    expect(onReset).toHaveBeenCalledWith("/api/data");
  });
});
