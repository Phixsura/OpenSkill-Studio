import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiGuardrailV2Panel } from "@/components/fleet-ai-guardrail-v2-panel";
describe("FleetAiGuardrailV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiGuardrailV2Panel engines={5} active={5} evals={200000000} blocked={50000} rules={500} />);
    expect(container.textContent).toContain("Guardrail v2");
}); });
