import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiIncidentV8Panel } from "@/components/fleet-ai-incident-v8-panel";
describe("FleetAiIncidentV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiIncidentV8Panel managers={3} active={3} incidents={20} mttr={3} auto={18} />);
    expect(container.textContent).toContain("Incident v8");
}); });
