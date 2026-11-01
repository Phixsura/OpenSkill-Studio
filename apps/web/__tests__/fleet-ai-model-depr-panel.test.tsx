import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelDeprPanel } from "@/components/fleet-ai-model-depr-panel";
describe("FleetAiModelDeprPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelDeprPanel managers={2} active={2} deprecated={30} migrated={28} sunsetDays={60} />);
    expect(container.textContent).toContain("Model Deprecation");
}); });
