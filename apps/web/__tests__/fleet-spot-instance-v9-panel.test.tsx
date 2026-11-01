import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSpotInstanceV9Panel } from "@/components/fleet-spot-instance-v9-panel";
describe("FleetSpotInstanceV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetSpotInstanceV9Panel instances={50} savings={70} />);
    expect(container.textContent).toContain("Spot Instance v9");
}); });
