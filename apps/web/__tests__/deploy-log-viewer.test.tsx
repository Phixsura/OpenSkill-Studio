import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployLogViewer } from "@/components/deploy-log-viewer";

describe("DeployLogViewer", () => {
  it("renders logs", () => {
    const { container } = render(
      <DeployLogViewer deployId="d1" total={3} errorCount={1} logs={[
        { seq: 0, level: "info", message: "Building image..." },
        { seq: 1, level: "info", message: "Pushing..." },
        { seq: 2, level: "error", message: "Health check failed" },
      ]} />
    );
    expect(container.textContent).toContain("Deploy Logs");
    expect(container.textContent).toContain("d1");
    expect(container.textContent).toContain("3 lines");
    expect(container.textContent).toContain("1 errors");
    expect(container.textContent).toContain("Building image...");
    expect(container.textContent).toContain("Health check failed");
  });
});
