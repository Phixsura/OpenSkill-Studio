import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiVideoAnalPanel } from "@/components/fleet-ai-video-anal-panel";
describe("FleetAiVideoAnalPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiVideoAnalPanel analyzers={5} active={5} hours={50000} fps={60} events={25000000} />);
    expect(container.textContent).toContain("Video Analysis");
}); });
