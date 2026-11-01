import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetBackupPanel } from "@/components/fleet-backup-panel";
describe("FleetBackupPanel", () => { it("renders", () => {
    const { container } = render(<FleetBackupPanel total={5} fresh={3} stale={2} failed={0} healthy={false} />);
    expect(container.textContent).toContain("Backups");
    expect(container.textContent).toContain("2 stale");
}); });
