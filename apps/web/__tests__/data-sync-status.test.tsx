import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DataSyncStatus } from "@/components/data-sync-status";

describe("DataSyncStatus", () => {
  it("renders sync", () => {
    const { container } = render(
      <DataSyncStatus totalSynced={500} totalFailed={10} successRate={98}
        jobs={[
          { source: "postgres", destination: "elastic", totalRecords: 1000, synced: 500, failed: 10, status: "running" },
        ]} />
    );
    expect(container.textContent).toContain("Data Sync");
    expect(container.textContent).toContain("98% success");
    expect(container.textContent).toContain("postgres → elastic");
    expect(container.textContent).toContain("500/1000");
  });
});
