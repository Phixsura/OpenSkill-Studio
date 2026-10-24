import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiGraceShutPanel } from "@/components/fleet-ai-grace-shut-panel";
describe("FleetAiGraceShutPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiGraceShutPanel managers={4} active={4} shutdowns={50} drained={200000} lost={0} />);
    expect(container.textContent).toContain("Graceful Shutdown");
}); });
