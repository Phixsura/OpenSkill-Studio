import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UsageReportCard } from "@/components/usage-report-card";

describe("UsageReportCard", () => {
  it("renders report", () => {
    const { container } = render(
      <UsageReportCard period="2026-10" apiCalls={50000} uniqueUsers={200} uptimePct={99.9}
        highlights={["🔥 50,000 API calls", "✅ 99.9%+ uptime"]} />
    );
    expect(container.textContent).toContain("50,000");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("2026-10");
    expect(container.textContent).toContain("99.9%+ uptime");
  });
});
