import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSreV7Panel } from "@/components/fleet-ai-sre-v7-panel";
describe("FleetAiSreV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiSreV7Panel teams={5} active={5} toil={10} budget={80} slos={200} mttr={3} />);
    expect(container.textContent).toContain("SRE v7");
}); });
