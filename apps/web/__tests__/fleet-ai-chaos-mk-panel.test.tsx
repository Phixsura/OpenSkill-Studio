import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiChaosMkPanel } from "@/components/fleet-ai-chaos-mk-panel";
describe("FleetAiChaosMkPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiChaosMkPanel monkeys={3} active={3} injections={200} recovered={198} unrecovered={2} recoveryRate={99} />);
    expect(container.textContent).toContain("Chaos Monkey");
}); });
