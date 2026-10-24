import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelAttestPanel } from "@/components/fleet-ai-model-attest-panel";
describe("FleetAiModelAttestPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelAttestPanel attestors={3} active={3} models={1000} signatures={1000} verifications={50000} />);
    expect(container.textContent).toContain("Model Attestation");
}); });
