import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiMusicGenPanel } from "@/components/fleet-ai-music-gen-panel";
describe("FleetAiMusicGenPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiMusicGenPanel generators={3} active={3} tracks={500000} genres={10} duration={240} />);
    expect(container.textContent).toContain("Music Generation");
}); });
