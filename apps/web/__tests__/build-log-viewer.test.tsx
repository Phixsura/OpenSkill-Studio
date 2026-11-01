import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { BuildLogViewer } from "@/components/build-log-viewer";

describe("BuildLogViewer", () => {
  const steps = [
    { name: "Install", status: "success", icon: "📦", durationDisplay: "5.0s", outputLines: 50 },
    { name: "Test", status: "failed", icon: "🧪", durationDisplay: "1.5s", outputLines: 120 },
  ];
  it("renders build steps", () => {
    const { container } = render(
      <BuildLogViewer steps={steps} overall="failed" totalDisplay="6.5s" failedStep="Test" />
    );
    expect(container.textContent).toContain("Install");
    expect(container.textContent).toContain("Test");
    expect(container.textContent).toContain("6.5s");
    expect(container.textContent).toContain("Failed at: Test");
  });
});
