import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDistillPanel } from "@/components/fleet-ai-distill-panel";
describe("FleetAiDistillPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDistillPanel jobs={6} active={6} teacherB={405} studentB={8} retention={93} />);
    expect(container.textContent).toContain("Distillation");
}); });
