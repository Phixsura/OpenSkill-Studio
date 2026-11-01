import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RateCtrlPanel } from "@/components/rate-ctrl-panel";
describe("RateCtrlPanel", () => {
  it("renders", () => {
    const { container } = render(
      <RateCtrlPanel currentLimit={1200} currentRps={600} headroomPct={50} action="increase" />
    );
    expect(container.textContent).toContain("Rate Controller");
    expect(container.textContent).toContain("increase");
    expect(container.textContent).toContain("1,200 rps");
    expect(container.textContent).toContain("600 rps");
    expect(container.textContent).toContain("50% headroom");
  });
});
