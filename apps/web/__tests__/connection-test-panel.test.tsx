import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ConnectionTestPanel } from "@/components/connection-test-panel";

describe("ConnectionTestPanel", () => {
  it("renders results", () => {
    const onTest = vi.fn();
    const { container, getByText } = render(
      <ConnectionTestPanel passed={2} total={2} allPassed={true} onTest={onTest}
        results={[
          { success: true, url: "https://api.example.com", hostname: "api.example.com", latencyMs: 45, tls: true },
          { success: true, url: "https://db.example.com", hostname: "db.example.com", latencyMs: 12, tls: true },
        ]} />
    );
    expect(container.textContent).toContain("Connection Tests");
    expect(container.textContent).toContain("2/2 passed");
    expect(container.textContent).toContain("api.example.com");
    expect(container.textContent).toContain("45ms");
    fireEvent.click(getByText("Retest"));
    expect(onTest).toHaveBeenCalled();
  });
});
