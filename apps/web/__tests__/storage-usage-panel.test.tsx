import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StorageUsagePanel } from "@/components/storage-usage-panel";
describe("StorageUsagePanel", () => {
  it("renders", () => {
    const { container } = render(
      <StorageUsagePanel totalGb={650} limitGb={1000} pctUsed={65}
        monthsUntilFull={7} byType={{ blob: 500, database: 150 }} />
    );
    expect(container.textContent).toContain("Storage Usage");
    expect(container.textContent).toContain("650GB / 1000GB");
    expect(container.textContent).toContain("65%");
    expect(container.textContent).toContain("7mo left");
    expect(container.textContent).toContain("blob: 500GB");
  });
});
