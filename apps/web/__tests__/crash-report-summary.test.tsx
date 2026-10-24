import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CrashReportSummary } from "@/components/crash-report-summary";

describe("CrashReportSummary", () => {
  const groups = [
    { signature: "abc", message: "NullPointer", count: 5, affected_users: 3, os_list: ["iOS", "Android"], last_seen: "2026-10-02" },
  ];
  it("renders", () => {
    const { container } = render(
      <CrashReportSummary totalCrashes={10} uniqueIssues={2} crashFreeRate={98.5} groups={groups} />
    );
    expect(container.textContent).toContain("Crash Reports");
    expect(container.textContent).toContain("10");
    expect(container.textContent).toContain("98.5%");
    expect(container.textContent).toContain("NullPointer");
    expect(container.textContent).toContain("5×");
  });
});
