import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MockServerPanel } from "@/components/mock-server-panel";

const mockEndpoints = [
  { id: "m1", method: "GET", pathPattern: "/api/users", statusCode: 200, callCount: 15, enabled: true, latencyMs: 0 },
  { id: "m2", method: "POST", pathPattern: "/api/data", statusCode: 201, callCount: 3, enabled: false, latencyMs: 500 },
];
const mockRequests = [
  { method: "GET", path: "/api/users", matchedEndpoint: "m1" },
  { method: "GET", path: "/api/users", matchedEndpoint: "m1" },
];

describe("MockServerPanel", () => {
  it("renders endpoints", () => {
    const { container } = render(
      <MockServerPanel endpoints={mockEndpoints} requests={mockRequests} />
    );
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("×15");
    expect(container.textContent).toContain("2 recorded");
  });

  it("shows requests tab", () => {
    const { getByText, container } = render(
      <MockServerPanel endpoints={mockEndpoints} requests={mockRequests} />
    );
    fireEvent.click(getByText("Requests (2)"));
    expect(container.textContent).toContain("/api/users");
  });

  it("calls onReset", () => {
    const onReset = vi.fn();
    const { getByText } = render(
      <MockServerPanel endpoints={mockEndpoints} requests={mockRequests} onReset={onReset} />
    );
    fireEvent.click(getByText("Reset"));
    expect(onReset).toHaveBeenCalled();
  });
});
