import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiWebhookQueueDepthMonitorCard from "../src/components/api-developer-api-api-webhook-queue-depth-monitor-card";

const snapshots = [
  { destination: "https://api.example.com/hook", depth: 2000, oldest_age_seconds: 600, estimated_drain_seconds: 200, backlogged: true },
  { destination: "https://fast.example.com/hook", depth: 10, oldest_age_seconds: 2, estimated_drain_seconds: 0.2, backlogged: false },
];

describe("APIDeveloperAPIApiWebhookQueueDepthMonitorCard", () => {
  it("shows queue depth", () => {
    const { container } = render(<APIDeveloperAPIApiWebhookQueueDepthMonitorCard snapshots={snapshots} totalDepth={2010} backloggedCount={1} appName="App" />);
    expect(container.textContent).toContain("Queue Depth");
    expect(container.textContent).toContain("2,010");
    expect(container.textContent).toContain("1 backlogged");
    expect(container.textContent).toContain("2000 msgs");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiWebhookQueueDepthMonitorCard snapshots={[]} totalDepth={0} backloggedCount={0} appName="App" />);
    expect(container.textContent).toContain("No queue data");
  });
});
