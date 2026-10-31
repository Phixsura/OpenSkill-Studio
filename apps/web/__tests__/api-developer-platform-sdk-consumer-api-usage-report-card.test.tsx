import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import UsageReportCard from "../src/components/api-developer-platform-sdk-consumer-api-usage-report-card";

describe("UsageReportCard", () => {
  it("renders title and reports", () => {
    const { container } = render(<UsageReportCard />);
    expect(container.textContent).toContain("Usage Reports");
    expect(container.textContent).toContain("Oct 2024");
    expect(container.textContent).toContain("Sep 2024");
  });

  it("shows status and count", () => {
    const { container } = render(<UsageReportCard />);
    expect(container.textContent).toContain("finalized");
    expect(container.textContent).toContain("draft");
    expect(container.textContent).toContain("3 reports");
  });
});
