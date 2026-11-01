import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCasPanel } from "@/components/fleet-cas-panel";
describe("FleetCasPanel", () => { it("renders", () => {
    const { container } = render(<FleetCasPanel totalEvents={10} scaleUps={5} scaleDowns={3} failed={2} healthy={false} />);
    expect(container.textContent).toContain("Cluster Autoscaler");
    expect(container.textContent).toContain("2 failed");
}); });
