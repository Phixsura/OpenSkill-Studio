import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RunbookExecPanel } from "@/components/runbook-exec-panel";

describe("RunbookExecPanel", () => {
  it("renders", () => {
    const { container } = render(
      <RunbookExecPanel name="restart_api" severity="standard" success={true}
        steps={[
          { step: "drain", status: "success" },
          { step: "restart", status: "success" },
          { step: "verify", status: "success" },
        ]} />
    );
    expect(container.textContent).toContain("Runbook: restart_api");
    expect(container.textContent).toContain("Done");
    expect(container.textContent).toContain("drain");
    expect(container.textContent).toContain("restart");
    expect(container.textContent).toContain("verify");
  });
});
