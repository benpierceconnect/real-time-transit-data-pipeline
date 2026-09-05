package com.benpierce.transitcdc;

import java.net.HttpURLConnection;
import java.net.URI;

public final class Healthcheck {
    private Healthcheck() {}

    public static void main(String[] args) {
        String target = args.length == 0 ? "http://127.0.0.1:8080/health" : args[0];
        try {
            HttpURLConnection connection = (HttpURLConnection) URI.create(target).toURL().openConnection();
            connection.setConnectTimeout(2_000);
            connection.setReadTimeout(2_000);
            connection.setRequestMethod("GET");
            connection.setRequestProperty("User-Agent", "transit-cdc-healthcheck/1.0");
            int statusCode = connection.getResponseCode();
            connection.disconnect();
            if (statusCode != 200) {
                System.err.println("CDC health endpoint returned HTTP " + statusCode);
                System.exit(1);
            }
        } catch (Exception exc) {
            System.err.println("CDC health check failed: " + exc.getMessage());
            System.exit(1);
        }
    }
}
