import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlaySbPanel } from "@/components/fleet-ai-play-sb-panel";
describe("FleetAiPlaySbPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlaySbPanel sandboxes={5} active={5} sessions={200000} duration={25} models={50} />);
    expect(container.textContent).toContain("Playground Sandbox");
}); });
