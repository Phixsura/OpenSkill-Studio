import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ConfigSyncPanel } from "@/components/config-sync-panel";
describe("ConfigSyncPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ConfigSyncPanel environments={3} totalKeys={15} inSync={false} different={["db_host", "cache"]} />
    );
    expect(container.textContent).toContain("Config Sync");
    expect(container.textContent).toContain("2 diffs");
    expect(container.textContent).toContain("db_host, cache");
  });
});
