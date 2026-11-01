import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAppwritePanel } from "@/components/fleet-appwrite-panel";
describe("FleetAppwritePanel", () => { it("renders", () => {
    const { container } = render(<FleetAppwritePanel projects={10} active={10} databases={20} storageGb={200} functions={50} />);
    expect(container.textContent).toContain("Appwrite");
}); });
