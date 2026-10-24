import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetImgPullPanel } from "@/components/fleet-img-pull-panel";
describe("FleetImgPullPanel", () => { it("renders", () => {
    const { container } = render(<FleetImgPullPanel total={100} avgPull={8000} slowPulls={5} failed={1} healthy={false} />);
    expect(container.textContent).toContain("Image Pulls");
    expect(container.textContent).toContain("Pull failures");
}); });
