package com.benpierce.transitcdc;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public final class HealthServer implements AutoCloseable {
    private final HttpServer server;
    private final ExecutorService executor;
    private final HealthState state;

    public HealthServer(int port, HealthState state) throws IOException {
        this.state = state;
        this.server = HttpServer.create(new InetSocketAddress(port), 0);
        this.server.createContext("/health", this::handleHealth);
        this.executor = Executors.newSingleThreadExecutor(runnable -> {
            Thread thread = new Thread(runnable, "health-server");
            thread.setDaemon(true);
            return thread;
        });
        this.server.setExecutor(executor);
    }

    public void start() {
        server.start();
    }

    private void handleHealth(HttpExchange exchange) throws IOException {
        Instant lastEvent = state.lastEventAt();
        String body = "{" +
                "\"status\":\"" + state.status() + "\"," +
                "\"processed_events\":" + state.processedCount() + "," +
                "\"failed_events\":" + state.failedCount() + "," +
                "\"last_event_at\":" + jsonString(lastEvent == null ? null : lastEvent.toString()) + "," +
                "\"last_error\":" + jsonString(state.lastError()) +
                "}";
        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().add("Content-Type", "application/json; charset=utf-8");
        exchange.sendResponseHeaders(state.ready() ? 200 : 503, bytes.length);
        exchange.getResponseBody().write(bytes);
        exchange.close();
    }

    private String jsonString(String value) {
        if (value == null) return "null";
        return "\"" + value.replace("\\", "\\\\").replace("\"", "\\\"") + "\"";
    }

    @Override
    public void close() {
        server.stop(0);
        executor.shutdownNow();
    }
}
