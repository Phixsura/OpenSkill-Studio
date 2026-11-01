import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RateLimitPolicyPanel } from "@/components/rate-limit-policy-panel";

const mockPolicies = [
  { id: "p1", endpoint: "/api/data", algorithm: "sliding_window" as const,
    maxRequests: 100, windowSeconds: 60, burstSize: 20, currentUsage: 75 },
  { id: "p2", endpoint: "/api/search", algorithm: "token_bucket" as const,
    maxRequests: 1000, windowSeconds: 3600, burstSize: 50, currentUsage: 200 },
];

describe("RateLimitPolicyPanel", () => {
  it("renders policies with limits", () => {
    const { container } = render(
      <RateLimitPolicyPanel policies={mockPolicies} extensionName="MyExt" />
    );
    expect(container.textContent).toContain("/api/data");
    expect(container.textContent).toContain("100 req/1m");
    expect(container.textContent).toContain("Sliding Window");
    expect(container.textContent).toContain("75%");
  });

  it("shows token bucket algorithm", () => {
    const { container } = render(
      <RateLimitPolicyPanel policies={mockPolicies} extensionName="Test" />
    );
    expect(container.textContent).toContain("Token Bucket");
    expect(container.textContent).toContain("1000 req/1h");
  });

  it("calls onEdit", () => {
    const onEdit = vi.fn();
    const { getAllByText } = render(
      <RateLimitPolicyPanel policies={mockPolicies} extensionName="Test" onEdit={onEdit} />
    );
    fireEvent.click(getAllByText("Edit")[0]);
    expect(onEdit).toHaveBeenCalledWith("p1");
  });
});
