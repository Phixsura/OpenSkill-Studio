import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UptimeCalcPanel } from "@/components/uptime-calc-panel";
describe("UptimeCalcPanel", () => {
  it("renders", () => {
    const { container } = render(
      <UptimeCalcPanel uptimePct={99.98} nines={4} downtimeMinutes={5}
        incidents={2} slaLabel="4-nines" />
    );
    expect(container.textContent).toContain("Uptime");
    expect(container.textContent).toContain("99.98%");
    expect(container.textContent).toContain("4-nines");
    expect(container.textContent).toContain("5min");
    expect(container.textContent).toContain("2");
  });
});
