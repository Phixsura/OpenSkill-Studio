import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EndpointRegistryPanel } from "@/components/endpoint-registry-panel";

const endpoints = [
  { path: "/users", method: "GET", version: "v1", description: "List",
    deprecated: false, callCount: 5000, avgLatencyMs: 45, tags: [] },
  { path: "/data", method: "POST", version: "v2", description: "Create",
    deprecated: false, callCount: 3000, avgLatencyMs: 80, tags: [] },
];
const stats = { total: 2, deprecated: 0, totalCalls: 8000, versions: ["v1", "v2"], extensions: 2 };

describe("EndpointRegistryPanel", () => {
  it("renders endpoints", () => {
    const { container } = render(<EndpointRegistryPanel endpoints={endpoints} stats={stats} />);
    expect(container.textContent).toContain("/users");
    expect(container.textContent).toContain("2 endpoints");
  });

  it("filters by version", () => {
    const { container } = render(<EndpointRegistryPanel endpoints={endpoints} stats={stats} />);
    const btns = container.querySelectorAll("button");
    const v2Btn = Array.from(btns).find(b => b.textContent === "v2" && b.className.includes("rounded-full"));
    if (v2Btn) fireEvent.click(v2Btn);
    // After filter, only v2 endpoints in the list area
    const rows = container.querySelectorAll("[class*='cursor-pointer']");
    expect(rows.length).toBe(1);
  });

  it("calls onSelect", () => {
    const fn = vi.fn();
    const { container } = render(<EndpointRegistryPanel endpoints={endpoints} stats={stats} onSelect={fn} />);
    const row = container.querySelector("[class*='cursor-pointer']");
    if (row) fireEvent.click(row);
    expect(fn).toHaveBeenCalled();
  });
});
