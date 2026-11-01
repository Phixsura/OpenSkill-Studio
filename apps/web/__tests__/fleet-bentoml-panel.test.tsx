import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetBentomlPanel } from "@/components/fleet-bentoml-panel";
describe("FleetBentomlPanel", () => { it("renders", () => {
    const { container } = render(<FleetBentomlPanel services={5} running={5} bentos={20} requests={2000000} />);
    expect(container.textContent).toContain("BentoML");
}); });
