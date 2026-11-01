import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiAccessGovV7Panel } from "@/components/fleet-ai-access-gov-v7-panel";
describe("FleetAiAccessGovV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiAccessGovV7Panel systems={3} active={3} users={500000} roles={1000} reviews={500} excessive={0} />);
    expect(container.textContent).toContain("Access Gov v7");
}); });
