import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AlertSilencePanel } from "@/components/alert-silence-panel";
describe("AlertSilencePanel", () => {
  it("renders", () => {
    const { container } = render(
      <AlertSilencePanel activeCount={1} silences={[{ name: "maint", matcher: "cpu_high", durationMinutes: 60, reason: "deploy" }]} />
    );
    expect(container.textContent).toContain("Alert Silences");
    expect(container.textContent).toContain("cpu_high");
    expect(container.textContent).toContain("60min");
  });
});
