import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiBackupRecPanel } from "@/components/fleet-ai-backup-rec-panel";
describe("FleetAiBackupRecPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiBackupRecPanel systems={3} active={3} backups={72} sizeTb={100} rpo={10} rto={20} />);
    expect(container.textContent).toContain("Backup");
}); });
