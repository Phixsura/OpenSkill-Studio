import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDevportalPanel } from "@/components/fleet-ai-devportal-panel";
describe("FleetAiDevportalPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDevportalPanel portals={3} active={3} docsPages={1000} apiKeys={50000} developers={20000} />);
    expect(container.textContent).toContain("AI Dev Portal");
}); });
