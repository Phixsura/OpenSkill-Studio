import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RunbookProgress } from "@/components/runbook-progress";

describe("RunbookProgress", () => {
  it("renders and executes", () => {
    const onExecute = vi.fn();
    const { container, getByText } = render(
      <RunbookProgress name="Deploy" status="in_progress" completed={1} total={2}
        onExecute={onExecute} steps={[
          { index: 0, title: "Health check", command: "curl /health", status: "passed", output: "OK" },
          { index: 1, title: "Restart", command: "systemctl restart", status: "pending", output: "" },
        ]} />
    );
    expect(container.textContent).toContain("Deploy");
    expect(container.textContent).toContain("1/2");
    expect(container.textContent).toContain("Health check");
    expect(container.textContent).toContain("OK");
    fireEvent.click(getByText("Run"));
    expect(onExecute).toHaveBeenCalledWith(1);
  });
});
