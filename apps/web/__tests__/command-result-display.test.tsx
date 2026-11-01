import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CommandResultDisplay } from "@/components/command-result-display";

describe("CommandResultDisplay", () => {
  it("success", () => {
    const { container } = render(
      <CommandResultDisplay command="npm test" exitCode={0} success={true}
        stdoutLines={["All tests passed"]} stderrLines={[]} durationFormatted="3.2s" />
    );
    expect(container.textContent).toContain("$ npm test");
    expect(container.textContent).toContain("✅");
    expect(container.textContent).toContain("exit 0");
    expect(container.textContent).toContain("3.2s");
    expect(container.textContent).toContain("All tests passed");
  });
  it("failure", () => {
    const { container } = render(
      <CommandResultDisplay command="npm build" exitCode={1} success={false}
        stdoutLines={[]} stderrLines={["Error: Not found"]} durationFormatted="500ms" />
    );
    expect(container.textContent).toContain("❌");
    expect(container.textContent).toContain("Error: Not found");
  });
});
