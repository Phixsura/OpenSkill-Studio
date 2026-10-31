import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PrioSchedPanel } from "@/components/prio-sched-panel";
describe("PrioSchedPanel", () => {
  it("renders", () => {
    const { container } = render(
      <PrioSchedPanel totalQueued={20} processed={1000}
        depths={{ critical: 2, high: 5, normal: 8, low: 3, background: 2 }} />
    );
    expect(container.textContent).toContain("Priority Scheduler");
    expect(container.textContent).toContain("20 queued");
    expect(container.textContent).toContain("1,000 processed");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("normal");
  });
});
