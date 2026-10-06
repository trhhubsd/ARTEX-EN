"use client";

import * as React from "react";

import Link from "next/link";

import { ArrowUpCircleIcon } from "lucide-react";

import { api } from "@/lib/api";

/**
 * In the top bar"New version"Tip: Check on page load; updates highlight next to version number，
 * Click to go to the “Version & Update” card on the system settings page。
 *
 * GitHub query results cached 30 min; safe to check on each mount
 * ——Unauthenticated GitHub API: 60 requests/hour/IP; without cache, opening many tabs may exceed limit
 * Will exhaust quota, preventing future updates。
 *
 * Silent on query failures; errors shown when user clicks “Check for Updates” in settings。
 */
export function UpdateBadge() {
  const [latest, setLatest] = React.useState("");

  React.useEffect(() => {
    let alive = true;
    api
      .checkUpdate()
      .then((r) => {
        // has_update 已经包含了"版本号可比较"的判断，开发构建不会亮这个提示。
        if (alive && r.has_update && r.latest) setLatest(r.latest.replace(/^v(?=\d)/, ""));
      })
      .catch(() => {
        // 静默：没网 / GitHub 限流都不该在顶栏弹错误。
      });
    return () => {
      alive = false;
    };
  }, []);

  if (!latest) return null;

  return (
    <Link
      href="/system/settings"
      title={`New version found ${latest}，Click to go to update`}
      className="inline-flex items-center gap-1.5 rounded-full bg-primary px-2.5 py-1 font-medium text-primary-foreground text-xs transition-opacity hover:opacity-90"
    >
      {/* 呼吸点：顶栏元素很多，纯文字容易被忽略，动效让它一眼可见。 */}
      <span className="relative flex size-1.5">
        <span className="absolute inline-flex size-full animate-ping rounded-full bg-primary-foreground opacity-75" />
        <span className="relative inline-flex size-1.5 rounded-full bg-primary-foreground" />
      </span>
      <ArrowUpCircleIcon className="size-3.5" />
      <span className="hidden sm:inline">New version {latest}</span>
      <span className="sm:hidden">New version</span>
    </Link>
  );
}
