import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployCadenceChart } from "@/components/deploy-cadence-chart";

describe("DeployCadenceChart", () => {
  it("renders", () => {
    const { container } = render(
      <DeployCadenceChart total={45} perDay={1.5} perWeek={10.5}
        doraLevel="elite" busiestDay="Monday"
        byEnvironment={{ production: 30, staging: 15 }} />
    );
    expect(container.textContent).toContain("Deploy Cadence");
    expect(container.textContent).toContain("DORA: elite");
    expect(container.textContent).toContain("45");
    expect(container.textContent).toContain("1.5");
    expect(container.textContent).toContain("Monday");
    expect(container.textContent).toContain("production: 30");
  });
});
