import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RuntimeConfigPanel } from "@/components/runtime-config-panel";

describe("RuntimeConfigPanel", () => {
  it("renders configs and changes", () => {
    const { container } = render(
      <RuntimeConfigPanel totalConfigs={5}
        configs={[
          { key: "feature.dark_mode", value: "true", env: "prod", version: "abc123" },
          { key: "db.pool_size", value: "20", env: "prod", version: "def456" },
        ]}
        recentChanges={[
          { key: "feature.dark_mode", old: "false", new: "true", changedBy: "alice" },
        ]} />
    );
    expect(container.textContent).toContain("Runtime Config");
    expect(container.textContent).toContain("5 configs");
    expect(container.textContent).toContain("feature.dark_mode");
    expect(container.textContent).toContain("true");
    expect(container.textContent).toContain("prod");
    expect(container.textContent).toContain("Recent Changes");
    expect(container.textContent).toContain("by alice");
  });
});
