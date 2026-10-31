import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetClusterBackupV9Panel } from "@/components/fleet-cluster-backup-v9-panel";
describe("FleetClusterBackupV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetClusterBackupV9Panel backups={10} ageHours={2} />);
    expect(container.textContent).toContain("Cluster Backup v9");
}); });
