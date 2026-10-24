import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RateLimitConfigPanel } from "@/components/rate-limit-config-panel";

describe("RateLimitConfigPanel", () => {
  const endpoints = [
    { method: "GET", path: "/api/apps", rpm: 600, burst: 50, custom: false },
    { method: "POST", path: "/api/apps", rpm: 60, burst: 10, custom: true },
  ];
  it("renders config", () => {
    const { container } = render(
      <RateLimitConfigPanel endpoints={endpoints} customCount={1} onEdit={vi.fn()} />
    );
    expect(container.textContent).toContain("Rate Limits");
    expect(container.textContent).toContain("/api/apps");
    expect(container.textContent).toContain("600 rpm");
    expect(container.textContent).toContain("custom");
    expect(container.textContent).toContain("1 custom");
  });
});
