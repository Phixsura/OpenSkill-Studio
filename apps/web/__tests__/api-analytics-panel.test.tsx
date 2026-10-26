import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiAnalyticsPanel } from "@/components/api-analytics-panel";

const mockSummary = { totalEndpoints: 10, totalHits: 50000, totalErrors: 500, overallErrorRate: 1.0, avgLatency: 45 };
const mockTop = [
  { method: "GET", endpoint: "/api/users", hits: 20000, avgLatency: 30, errorRate: 0.5 },
  { method: "POST", endpoint: "/api/data", hits: 15000, avgLatency: 80, errorRate: 2.0 },
];

describe("ApiAnalyticsPanel", () => {
  it("renders summary", () => {
    const { container } = render(
      <ApiAnalyticsPanel summary={mockSummary} topEndpoints={mockTop} slowest={[]} errorProne={[]} />
    );
    expect(container.textContent).toContain("50,000");
    expect(container.textContent).toContain("1%");
    expect(container.textContent).toContain("45ms");
  });

  it("shows top endpoints", () => {
    const { container } = render(
      <ApiAnalyticsPanel summary={mockSummary} topEndpoints={mockTop} slowest={[]} errorProne={[]} />
    );
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("20000 hits");
  });

  it("switches tabs", () => {
    const slow = [{ method: "GET", endpoint: "/api/slow", hits: 100, avgLatency: 5000, errorRate: 0 }];
    const { getByText, container } = render(
      <ApiAnalyticsPanel summary={mockSummary} topEndpoints={mockTop} slowest={slow} errorProne={[]} />
    );
    fireEvent.click(getByText("Slowest"));
    expect(container.textContent).toContain("/api/slow");
    expect(container.textContent).toContain("5000ms");
  });
});
