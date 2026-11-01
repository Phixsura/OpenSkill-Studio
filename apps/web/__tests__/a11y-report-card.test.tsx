import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { A11yReportCard } from "@/components/a11y-report-card";

describe("A11yReportCard", () => {
  it("renders report", () => {
    const { container } = render(
      <A11yReportCard totalPassed={5} totalFailed={1} results={[
        { component: "submit_btn", issues: [], passes: true },
        { component: "icon_btn", issues: [{ rule: "label", severity: "error", message: "Missing label" }], passes: false },
      ]} />
    );
    expect(container.textContent).toContain("Accessibility");
    expect(container.textContent).toContain("5 passed");
    expect(container.textContent).toContain("1 failed");
    expect(container.textContent).toContain("submit_btn");
    expect(container.textContent).toContain("Missing label");
  });
});
