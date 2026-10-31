import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TestReportCard } from "@/components/test-report-card";

describe("TestReportCard", () => {
  it("shows stats", () => {
    const { container } = render(
      <TestReportCard appName="MyApp" passRate={80} passed={8} failed={2} generatedAt="2026-01-01T00:00:00Z" />
    );
    expect(container.textContent).toContain("MyApp");
    expect(container.textContent).toContain("80%");
    expect(container.textContent).toContain("8 passed");
    expect(container.textContent).toContain("2 failed");
  });
  it("green on 100%", () => {
    const { container } = render(
      <TestReportCard appName="X" passRate={100} passed={10} failed={0} generatedAt="2026-01-01T00:00:00Z" />
    );
    expect(container.querySelector("[class*='green']")).toBeTruthy();
  });
});
