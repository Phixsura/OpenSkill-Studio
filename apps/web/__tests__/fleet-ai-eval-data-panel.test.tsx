import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiEvalDataPanel } from "@/components/fleet-ai-eval-data-panel";
describe("FleetAiEvalDataPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiEvalDataPanel managers={3} active={3} datasets={200} samples={50000000} domains={40} />);
    expect(container.textContent).toContain("Eval Dataset");
}); });
