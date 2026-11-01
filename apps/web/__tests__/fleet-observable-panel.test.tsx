import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetObservablePanel } from "@/components/fleet-observable-panel";
describe("FleetObservablePanel", () => { it("renders", () => {
    const { container } = render(<FleetObservablePanel notebooks={20} published={20} cells={500} views={200000} />);
    expect(container.textContent).toContain("Observable");
}); });
