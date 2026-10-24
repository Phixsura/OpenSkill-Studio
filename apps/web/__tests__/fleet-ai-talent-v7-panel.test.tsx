import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTalentV7Panel } from "@/components/fleet-ai-talent-v7-panel";
describe("FleetAiTalentV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiTalentV7Panel systems={3} active={3} engineers={1000} hiring={100} retention={97} />);
    expect(container.textContent).toContain("Talent v7");
}); });
