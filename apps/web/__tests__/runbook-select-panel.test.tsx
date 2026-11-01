import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RunbookSelectPanel } from "@/components/runbook-select-panel";
describe("RunbookSelectPanel", () => {
  it("renders", () => {
    const { container } = render(
      <RunbookSelectPanel selected="restart_api" confidence={11} totalMatches={2}
        alternatives={[{ runbook: "scale_up", score: 5, steps: 3 }]} />
    );
    expect(container.textContent).toContain("Runbook Selector");
    expect(container.textContent).toContain("2 matches");
    expect(container.textContent).toContain("Selected: restart_api");
    expect(container.textContent).toContain("confidence: 11");
    expect(container.textContent).toContain("Also: scale_up");
  });
});
