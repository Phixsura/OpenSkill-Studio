import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDistLockPanel } from "@/components/fleet-ai-dist-lock-panel";
describe("FleetAiDistLockPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDistLockPanel managers={3} active={3} locks={100} acquisitions={2000000} contentions={5} />);
    expect(container.textContent).toContain("Distributed Lock");
}); });
