import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDbtPanel } from "@/components/fleet-dbt-panel";
describe("FleetDbtPanel", () => { it("renders", () => {
    const { container } = render(<FleetDbtPanel projects={10} passing={9} failed={1} models={500} tests={1200} />);
    expect(container.textContent).toContain("dbt");
    expect(container.textContent).toContain("1 failed");
}); });
