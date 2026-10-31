import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetClearmlPanel } from "@/components/fleet-clearml-panel";
describe("FleetClearmlPanel", () => { it("renders", () => {
    const { container } = render(<FleetClearmlPanel servers={3} running={3} tasks={15000} workers={50} />);
    expect(container.textContent).toContain("ClearML");
}); });
