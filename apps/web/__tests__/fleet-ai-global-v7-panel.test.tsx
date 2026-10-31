import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiGlobalV7Panel } from "@/components/fleet-ai-global-v7-panel";
describe("FleetAiGlobalV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiGlobalV7Panel systems={5} active={5} regions={30} countries={150} languages={50} />);
    expect(container.textContent).toContain("Global v7");
}); });
