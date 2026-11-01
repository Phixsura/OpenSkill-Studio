import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetImgAgePanel } from "@/components/fleet-img-age-panel";
describe("FleetImgAgePanel", () => { it("renders", () => {
    const { container } = render(<FleetImgAgePanel total={10} old={3} ancient={1} fresh={7} needsUpdate={true} />);
    expect(container.textContent).toContain("Image Age");
    expect(container.textContent).toContain("1 images");
}); });
