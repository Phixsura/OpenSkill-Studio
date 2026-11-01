import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetStoryblokPanel } from "@/components/fleet-storyblok-panel";
describe("FleetStoryblokPanel", () => { it("renders", () => {
    const { container } = render(<FleetStoryblokPanel spaces={3} active={3} stories={15000} components={200} />);
    expect(container.textContent).toContain("Storyblok");
}); });
