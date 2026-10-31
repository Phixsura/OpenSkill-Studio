import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ProfilerPanel } from "@/components/profiler-panel";

const mockSummary = { status: "completed", totalTimeMs: 1500, totalFunctions: 5, totalCalls: 250, totalMemoryKb: 2048 };
const mockHotspots = [
  { functionName: "processData", file: "worker.py", line: 42, totalTimeMs: 800, selfTimeMs: 600, callCount: 10, avgTimeMs: 80, memoryDeltaKb: 500 },
  { functionName: "fetchAPI", file: "api.py", line: 15, totalTimeMs: 500, selfTimeMs: 450, callCount: 5, avgTimeMs: 100, memoryDeltaKb: 200 },
];

describe("ProfilerPanel", () => {
  it("renders summary stats", () => {
    const { container } = render(
      <ProfilerPanel summary={mockSummary} hotspots={mockHotspots} byCalls={mockHotspots} isProfiling={false} />
    );
    expect(container.textContent).toContain("1500ms");
    expect(container.textContent).toContain("250");
    expect(container.textContent).toContain("2048KB");
  });

  it("shows hotspots with bars", () => {
    const { container } = render(
      <ProfilerPanel summary={mockSummary} hotspots={mockHotspots} byCalls={[]} isProfiling={false} />
    );
    expect(container.textContent).toContain("processData");
    expect(container.textContent).toContain("600ms");
    expect(container.textContent).toContain("×10");
  });

  it("shows profiling indicator", () => {
    const onStop = vi.fn();
    const { getByText } = render(
      <ProfilerPanel summary={null} hotspots={[]} byCalls={[]} isProfiling={true} onStop={onStop} />
    );
    fireEvent.click(getByText("Stop"));
    expect(onStop).toHaveBeenCalled();
  });

  it("calls onStart", () => {
    const onStart = vi.fn();
    const { getByText } = render(
      <ProfilerPanel summary={null} hotspots={[]} byCalls={[]} isProfiling={false} onStart={onStart} />
    );
    fireEvent.click(getByText("Start Profiling"));
    expect(onStart).toHaveBeenCalled();
  });
});
