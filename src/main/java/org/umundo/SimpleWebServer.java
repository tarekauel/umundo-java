package org.umundo;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;
import org.apache.commons.io.IOUtils;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;

public class SimpleWebServer {

  public static void main(int port) throws Exception {
    HttpServer server = HttpServer.create(new InetSocketAddress(port), 0);
    server.createContext("/", new Handler());
    server.setExecutor(null);
    server.start();
  }

  private static class Handler implements HttpHandler {
    @Override
    public void handle(HttpExchange t) throws IOException {
      String path = t.getRequestURI().toASCIIString();
      if (path.equals("/")) {
        path = "/index.html";
      }
      ClassLoader classLoader = getClass().getClassLoader();
      String response = IOUtils.toString(classLoader.getResourceAsStream("web" + path));
      t.sendResponseHeaders(200, response.length());
      OutputStream os = t.getResponseBody();
      os.write(response.getBytes());
      os.close();
    }
  }

}