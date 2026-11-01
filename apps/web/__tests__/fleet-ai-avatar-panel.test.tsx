import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiAvatarPanel } from "@/components/fleet-ai-avatar-panel";
describe("FleetAiAvatarPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiAvatarPanel services={5} active={5} avatars={200000} animations={800000} />);
    expect(container.textContent).toContain("AI Avatar");
}); });
