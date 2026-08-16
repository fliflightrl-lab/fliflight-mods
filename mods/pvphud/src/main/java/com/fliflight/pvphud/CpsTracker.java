package com.fliflight.pvphud;

import java.util.ArrayDeque;
import java.util.Deque;

/**
 * Tracks clicks per second (CPS) for left (attack) and right (use) buttons
 * using a sliding 1-second window of timestamps.
 */
public class CpsTracker {
    private static final long WINDOW_MS = 1000L;
    private static final Deque<Long> leftClicks = new ArrayDeque<>();
    private static final Deque<Long> rightClicks = new ArrayDeque<>();

    public static void onLeftClick() {
        record(leftClicks);
    }

    public static void onRightClick() {
        record(rightClicks);
    }

    private static void record(Deque<Long> clicks) {
        long now = System.currentTimeMillis();
        clicks.addLast(now);
        // prune old entries outside the 1-second window
        while (!clicks.isEmpty() && now - clicks.peekFirst() > WINDOW_MS) {
            clicks.pollFirst();
        }
    }

    public static int getLeftCps() {
        return pruneAndCount(leftClicks);
    }

    public static int getRightCps() {
        return pruneAndCount(rightClicks);
    }

    private static int pruneAndCount(Deque<Long> clicks) {
        long now = System.currentTimeMillis();
        while (!clicks.isEmpty() && now - clicks.peekFirst() > WINDOW_MS) {
            clicks.pollFirst();
        }
        return clicks.size();
    }
}
