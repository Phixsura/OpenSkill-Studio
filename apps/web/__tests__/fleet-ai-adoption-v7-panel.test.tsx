import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiAdoptionV7Panel } from "@/components/fleet-ai-adoption-v7-panel";
describe("FleetAiAdoptionV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiAdoptionV7Panel trackers={3} active={3} signups={200000} activated={100000} retained={80000} conversion={50} />);
    expect(container.textContent).toContain("Adoption v7");
}); });
