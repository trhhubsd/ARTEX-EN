"use client";

import * as React from "react";

import Link from "next/link";

import { ArrowUpCircleIcon } from "lucide-react";

import { api } from "@/lib/api";

/**
 * Top bar "new version" notice: checked once on full page load; when an update is
 * available it shows next to the version number, and clicking goes to the
 * "Version & Update" card on the system settings page.
 *
 * The backend caches GitHub query results for 30 minutes, so checking on every mount
 * is safe: the unauthenticated GitHub API only allows 60 requests/hour/IP, and without
 * that cache, opening several tabs could exhaust the quota and hide future updates.
 *
 * Silent on query failure; errors show only when the user clicks "Check for Updates" in settings.
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
      title={`New version found ${latest}; click to update`}
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
