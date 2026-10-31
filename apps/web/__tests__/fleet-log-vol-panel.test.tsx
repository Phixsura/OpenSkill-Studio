import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetLogVolPanel } from "@/components/fleet-log-vol-panel";
describe("FleetLogVolPanel", () => { it("renders", () => {
    const { container } = render(<FleetLogVolPanel totalGb={250} dailyCost={125} sources={10} expensive={true} />);
    expect(container.textContent).toContain("Log Volume");
    expect(container.textContent).toContain("High log costs");
}); });
