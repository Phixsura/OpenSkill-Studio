import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelGovV7Panel } from "@/components/fleet-ai-model-gov-v7-panel";
describe("FleetAiModelGovV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelGovV7Panel systems={3} active={3} models={2000} approved={1980} rejected={20} compliance={99.8} />);
    expect(container.textContent).toContain("Model Gov v7");
}); });
