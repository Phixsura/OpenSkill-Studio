import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PlaygroundConsole } from "@/components/playground-console";

describe("PlaygroundConsole", () => {
  it("renders console", () => {
    const { container } = render(
      <PlaygroundConsole sessionId="play_abc123def456" onSend={vi.fn()}
        variables={{ app_id: "test123" }}
        history={[
          { method: "GET", path: "/api/apps", status: 200, durationMs: 85 },
          { method: "POST", path: "/api/apps", status: 201, durationMs: 120 },
        ]} />
    );
    expect(container.textContent).toContain("API Playground");
    expect(container.textContent).toContain("2 requests");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("/api/apps");
    expect(container.textContent).toContain("app_id=test123");
  });
});
