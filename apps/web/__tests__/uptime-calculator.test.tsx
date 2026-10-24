import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UptimeCalculator } from "@/components/uptime-calculator";

describe("UptimeCalculator", () => {
  it("renders", () => {
    const { container } = render(
      <UptimeCalculator uptimePct={99.99} nines={4} downtimeMonthSec={259}
        downtimeYearSec={3153} display="99.99% (4 nines)" targetPct={99.9} met={true} />
    );
    expect(container.textContent).toContain("99.99%");
    expect(container.textContent).toContain("4 nines");
    expect(container.textContent).toContain("99.9%");
    expect(container.textContent).toContain("259s");
    expect(container.textContent).toContain("3153s");
  });
});
