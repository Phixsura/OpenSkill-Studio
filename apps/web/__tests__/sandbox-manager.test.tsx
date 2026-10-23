import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SandboxManager } from "@/components/sandbox-manager";

describe("SandboxManager", () => {
  it("renders sandboxes", () => {
    const onDestroy = vi.fn();
    const { container, getByText } = render(
      <SandboxManager onCreate={vi.fn()} onDestroy={onDestroy}
        sandboxes={[
          { id: "sbx_abc", name: "test-env", baseUrl: "https://sandbox-sbx_abc.api.openskill.io",
            status: "ready", requestCount: 42 },
        ]} />
    );
    expect(container.textContent).toContain("Sandboxes");
    expect(container.textContent).toContain("test-env");
    expect(container.textContent).toContain("42 requests");
    expect(container.textContent).toContain("ready");
    fireEvent.click(getByText("Delete"));
    expect(onDestroy).toHaveBeenCalledWith("sbx_abc");
  });
});
