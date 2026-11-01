import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiLifecyclePanel } from "@/components/fleet-ai-lifecycle-panel";
describe("FleetAiLifecyclePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiLifecyclePanel managers={3} active={3} models={200} stages={{dev: 40, staging: 20, production: 120, retired: 20}} />);
    expect(container.textContent).toContain("Model Lifecycle");
}); });
