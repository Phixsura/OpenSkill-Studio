import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiEthicsV7Panel } from "@/components/fleet-ai-ethics-v7-panel";
describe("FleetAiEthicsV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiEthicsV7Panel systems={3} active={3} assessments={1000} principles={50} score={98} />);
    expect(container.textContent).toContain("Ethics v7");
}); });
