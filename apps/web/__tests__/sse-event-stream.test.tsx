import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SseEventStream } from "@/components/sse-event-stream";

describe("SseEventStream", () => {
  it("renders stream", () => {
    const { container } = render(
      <SseEventStream channel="deploys" latestId={2} connected={true}
        events={[
          { type: "deploy.started", id: 1, data: { version: "2.0" } },
          { type: "deploy.completed", id: 2, data: { version: "2.0" } },
        ]} />
    );
    expect(container.textContent).toContain("deploys");
    expect(container.textContent).toContain("Connected");
    expect(container.textContent).toContain("#2");
    expect(container.textContent).toContain("deploy.started");
    expect(container.textContent).toContain("deploy.completed");
  });
});
