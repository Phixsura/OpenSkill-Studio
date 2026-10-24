import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GwLoadPanel } from "@/components/gw-load-panel";
describe("GwLoadPanel", () => {
  it("renders", () => {
    const { container } = render(
      <GwLoadPanel connUtilPct={80} rpsUtilPct={60} cpuPct={75}
        overallLoadPct={80} status="high" rps={30000} connections={8000} />
    );
    expect(container.textContent).toContain("Gateway Load: HIGH");
    expect(container.textContent).toContain("80%");
    expect(container.textContent).toContain("60%");
    expect(container.textContent).toContain("75%");
    expect(container.textContent).toContain("30,000");
    expect(container.textContent).toContain("8,000");
  });
});
