import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ConfigDiffViewer } from "@/components/config-diff-viewer";

describe("ConfigDiffViewer", () => {
  const diffs = [
    { key: "LOG_LEVEL", type: "changed", staging: "debug", production: "info" },
    { key: "REDIS_URL", type: "added", production: "redis://prod" },
  ];
  it("renders", () => {
    const { container } = render(
      <ConfigDiffViewer envA="staging" envB="production" diffs={diffs} sameCount={1} driftPct={66.7} />
    );
    expect(container.textContent).toContain("staging vs production");
    expect(container.textContent).toContain("66.7% drift");
    expect(container.textContent).toContain("LOG_LEVEL");
    expect(container.textContent).toContain("REDIS_URL");
  });
});
