import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-event-replay-buffer-card";

describe("EventReplayBufferCard", () => {
  it("shows buffer info", () => {
    const { container } = render(<Card totalBuffered={5000} pendingReplay={200} bufferSizeKb={512} maxBufferSize={10000} appName="App" />);
    expect(container.textContent).toContain("Replay Buffer");
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("200 pending");
    expect(container.textContent).toContain("512 KB");
  });
  it("no pending badge when zero", () => {
    const { container } = render(<Card totalBuffered={0} pendingReplay={0} bufferSizeKb={0} maxBufferSize={10000} appName="App" />);
    expect(container.textContent).not.toContain("pending");
  });
});
