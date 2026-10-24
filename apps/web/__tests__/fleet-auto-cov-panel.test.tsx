import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAutoCovPanel } from "@/components/fleet-auto-cov-panel";
describe("FleetAutoCovPanel", () => { it("renders", () => {
    const { container } = render(<FleetAutoCovPanel total={50} automated={40} manual={10} coveragePct={80} mature={true} />);
    expect(container.textContent).toContain("Automation Coverage");
    expect(container.textContent).toContain("80%");
}); });
