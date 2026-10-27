import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TelemetryDashboard } from "@/components/telemetry-dashboard";

const MOCK_SUMMARY = {
  installation_id: "inst-1",
  total_metrics: 1250,
  total_errors: 15,
  total_spans: 340,
  error_rate: 0.94,
  avg_span_ms: 125.5,
  top_errors: [
    ["ValueError", 8],
    ["TimeoutError", 5],
    ["KeyError", 2],
  ] as [string, number][],
  top_slow_ops: [
    ["db_query", 450.2],
    ["api_call", 220.0],
    ["render", 55.0],
  ] as [string, number][],
};

const EMPTY_SUMMARY = {
  installation_id: "inst-2",
  total_metrics: 0,
  total_errors: 0,
  total_spans: 0,
  error_rate: 0,
  avg_span_ms: 0,
  top_errors: [] as [string, number][],
  top_slow_ops: [] as [string, number][],
};

describe("TelemetryDashboard", () => {
  it("renders heading and app name", () => {
    const { container } = render(
      <TelemetryDashboard
        summary={MOCK_SUMMARY}
        appName="My App"
        quotaUsed={500}
        quotaLimit={10000}
      />,
    );
    expect(container.textContent).toContain("Telemetry");
    expect(container.textContent).toContain("My App");
  });

  it("renders stat tiles", () => {
    const { container } = render(
      <TelemetryDashboard summary={MOCK_SUMMARY} appName="App" quotaUsed={0} quotaLimit={10000} />,
    );
    expect(container.textContent).toContain("1,250");
    expect(container.textContent).toContain("15");
    expect(container.textContent).toContain("340");
    expect(container.textContent).toContain("0.94%");
    expect(container.textContent).toContain("125.5ms");
  });

  it("renders quota bar", () => {
    const { container } = render(
      <TelemetryDashboard
        summary={MOCK_SUMMARY}
        appName="App"
        quotaUsed={8000}
        quotaLimit={10000}
      />,
    );
    expect(container.textContent).toContain("8,000/10,000");
  });

  it("renders top errors", () => {
    const { container } = render(
      <TelemetryDashboard summary={MOCK_SUMMARY} appName="App" quotaUsed={0} quotaLimit={10000} />,
    );
    expect(container.textContent).toContain("Top Errors");
    expect(container.textContent).toContain("ValueError");
    expect(container.textContent).toContain("8×");
    expect(container.textContent).toContain("TimeoutError");
  });

  it("renders slowest operations", () => {
    const { container } = render(
      <TelemetryDashboard summary={MOCK_SUMMARY} appName="App" quotaUsed={0} quotaLimit={10000} />,
    );
    expect(container.textContent).toContain("Slowest Operations");
    expect(container.textContent).toContain("db_query");
    expect(container.textContent).toContain("450.2ms");
  });

  it("shows no errors state", () => {
    const { container } = render(
      <TelemetryDashboard summary={EMPTY_SUMMARY} appName="App" quotaUsed={0} quotaLimit={10000} />,
    );
    expect(container.textContent).toContain("No errors");
  });

  it("shows no spans state", () => {
    const { container } = render(
      <TelemetryDashboard summary={EMPTY_SUMMARY} appName="App" quotaUsed={0} quotaLimit={10000} />,
    );
    expect(container.textContent).toContain("No spans");
  });

  it("shows slow label for high avg span", () => {
    const slowSummary = { ...MOCK_SUMMARY, avg_span_ms: 600 };
    const { container } = render(
      <TelemetryDashboard summary={slowSummary} appName="App" quotaUsed={0} quotaLimit={10000} />,
    );
    expect(container.textContent).toContain("slow");
  });

  it("renders ranking numbers", () => {
    const { container } = render(
      <TelemetryDashboard summary={MOCK_SUMMARY} appName="App" quotaUsed={0} quotaLimit={10000} />,
    );
    expect(container.textContent).toContain("1.");
    expect(container.textContent).toContain("2.");
    expect(container.textContent).toContain("3.");
  });
});
