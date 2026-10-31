import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCommunityPanel } from "@/components/fleet-community-panel";
describe("FleetCommunityPanel", () => { it("renders", () => {
    const { container } = render(<FleetCommunityPanel stars={5000} forks={500} contributors={50} score={60} vibrant={true} />);
    expect(container.textContent).toContain("Community");
    expect(container.textContent).toContain("Vibrant");
}); });
