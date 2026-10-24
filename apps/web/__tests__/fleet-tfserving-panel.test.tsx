import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTfservingPanel } from "@/components/fleet-tfserving-panel";
describe("FleetTfservingPanel", () => { it("renders", () => {
    const { container } = render(<FleetTfservingPanel instances={5} serving={5} models={30} batchesPerSec={25000} />);
    expect(container.textContent).toContain("TF Serving");
}); });
