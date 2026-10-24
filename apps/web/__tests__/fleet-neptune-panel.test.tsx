import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetNeptunePanel } from "@/components/fleet-neptune-panel";
describe("FleetNeptunePanel", () => { it("renders", () => {
    const { container } = render(<FleetNeptunePanel projects={5} active={5} runs={50000} storageGb={200} />);
    expect(container.textContent).toContain("Neptune");
}); });
