import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetModalPanel } from "@/components/fleet-modal-panel";
describe("FleetModalPanel", () => { it("renders", () => {
    const { container } = render(<FleetModalPanel apps={10} running={10} gpuHours={1000} functions={200} />);
    expect(container.textContent).toContain("Modal");
}); });
