import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTestingV7Panel } from "@/components/fleet-ai-testing-v7-panel";
describe("FleetAiTestingV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiTestingV7Panel systems={5} active={5} tests={2000000} coverage={98} flaky={0.1} />);
    expect(container.textContent).toContain("Testing v7");
}); });
