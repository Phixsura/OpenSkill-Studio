import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiImagegenPanel } from "@/components/fleet-ai-imagegen-panel";
describe("FleetAiImagegenPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiImagegenPanel services={3} active={3} images={1500000} avgGenSec={8} />);
    expect(container.textContent).toContain("AI Image Gen");
}); });
