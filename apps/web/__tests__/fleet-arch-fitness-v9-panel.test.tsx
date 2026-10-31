import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetArchFitnessV9Panel } from "@/components/fleet-arch-fitness-v9-panel";
describe("FleetArchFitnessV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetArchFitnessV9Panel total={30} passing={30} />);
    expect(container.textContent).toContain("Arch Fitness v9");
}); });
