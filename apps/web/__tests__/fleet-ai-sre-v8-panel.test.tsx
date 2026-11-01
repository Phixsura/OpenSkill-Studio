import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSreV8Panel } from "@/components/fleet-ai-sre-v8-panel";
describe("FleetAiSreV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiSreV8Panel teams={5} active={5} toil={8} budget={85} slos={500} />);
    expect(container.textContent).toContain("SRE v8");
}); });
