import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TimeoutAlert } from "@/components/timeout-alert";

describe("TimeoutAlert", () => {
  it("shows function name", () => {
    const { container } = render(<TimeoutAlert functionName="sync_data" timeoutSeconds={30} elapsedSeconds={35.2} />);
    expect(container.textContent).toContain("sync_data");
  });

  it("shows timeout", () => {
    const { container } = render(<TimeoutAlert functionName="x" timeoutSeconds={60} elapsedSeconds={65} />);
    expect(container.textContent).toContain("60s");
  });

  it("shows elapsed", () => {
    const { container } = render(<TimeoutAlert functionName="x" timeoutSeconds={30} elapsedSeconds={42.5} />);
    expect(container.textContent).toContain("42.5s");
  });
});
