import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiEthicsV8Panel } from "@/components/fleet-ai-ethics-v8-panel";
describe("FleetAiEthicsV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiEthicsV8Panel systems={3} active={3} assessments={5000} principles={100} score={99} />);
    expect(container.textContent).toContain("Ethics v8");
}); });
