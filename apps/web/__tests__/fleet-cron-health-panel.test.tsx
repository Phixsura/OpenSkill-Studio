import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCronHealthPanel } from "@/components/fleet-cron-health-panel";
describe("FleetCronHealthPanel", () => { it("renders", () => {
    const { container } = render(<FleetCronHealthPanel total={10} onTime={8} delayed={1} failed={1} healthy={false} />);
    expect(container.textContent).toContain("Cron Jobs");
    expect(container.textContent).toContain("Issues detected");
}); });
