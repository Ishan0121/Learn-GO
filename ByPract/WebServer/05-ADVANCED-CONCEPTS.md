# Chapter 5: Advanced Concepts



<div align="center">
  <audio controls src="audio/05-ADVANCED-CONCEPTS.wav" title="Go Learning Audio Session" style="width: 100%; max-width: 400px; margin-bottom: 20px;"></audio>
  <p><i>Listen to the audio version above!</i></p>
</div>

A basic server is great for a local side project. But putting a server on the Internet requires handling edge cases, testing, and modern communication protocols.

## 1. Graceful Shutdown (The Polite Exit)

When you update your server code and restart the app (or when a cloud provider like AWS/Kubernetes recycles your container), a raw `SIGTERM` kill signal is sent to the process. 

If you just let the server die instantly, anyone who was in the middle of uploading a photo, paying for a product, or running a slow database query will get disconnected instantly, resulting in corrupted data or angry users.

A **Graceful Shutdown** catches that kill signal, stops accepting *new* traffic, finishes serving the *current* traffic, and *then* exits.

```go
package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"
)

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		time.Sleep(3 * time.Second) // Simulate a slow process
		w.Write([]byte("Task finished!"))
	})

	srv := &http.Server{
		Addr:    ":8080",
		Handler: mux,
	}

	// 1. Start the server in a Goroutine so it doesn't block the main thread
	go func() {
		fmt.Println("🚀 Server listening on :8080")
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Server crashed: %s\n", err)
		}
	}()

	// 2. Create a channel to listen for OS interrupt signals (Ctrl+C, Docker stop)
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGTERM)
	
	// 3. The main thread BLOCKS here until a signal is received
	<-stop 
	fmt.Println("\n🛑 Shutdown signal received! Stopping new requests...")

	// 4. Create a context with a 10-second timeout. 
	// We give active requests 10 seconds to finish before we forcibly kill them.
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// 5. Shutdown gracefully!
	if err := srv.Shutdown(ctx); err != nil {
		log.Printf("❌ Forced Shutdown due to error: %v\n", err)
	}
	
	fmt.Println("✅ Server exited safely")
}
```

## 2. CORS (Cross-Origin Resource Sharing)

If you have a React frontend running on `http://localhost:3000` and a Go backend on `http://localhost:8080`, your browser will physically block the React app from talking to the Go app. This is a security feature to prevent malicious websites from stealing data.

To fix this, the Go backend must send **CORS Headers** saying: *"I explicitly allow localhost:3000 to talk to me."*

We usually do this via a Middleware:

```go
func CorsMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Allow any website to hit this API (dangerous in prod, change * to your frontend URL)
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

		// If it's an OPTIONS request (a pre-flight check by the browser), return OK immediately
		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusOK)
			return
		}

		next.ServeHTTP(w, r)
	})
}
```

## 3. WebSockets (Real-Time Communication)

HTTP is unidirectional: The client asks, the server answers. 
But what if you are building a Chat App or a Live Stock Ticker? The server needs to push data to the client *without* being asked.

For this, we "upgrade" the HTTP connection into a persistent **WebSocket** connection. Go doesn't have websockets built-in, so the entire community uses the `gorilla/websocket` package.

```go
// go get github.com/gorilla/websocket

import (
	"github.com/gorilla/websocket"
	"net/http"
)

// The Upgrader converts the HTTP connection into a WebSocket connection
var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool { return true }, // Allow all origins for this example
}

func chatHandler(w http.ResponseWriter, r *http.Request) {
	// Upgrade the connection!
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		return // Connection failed
	}
	defer conn.Close()

	// An infinite loop to constantly listen for new messages from the client
	for {
		messageType, p, err := conn.ReadMessage()
		if err != nil {
			return // Client disconnected
		}
		
		// Echo the message back to them
		err = conn.WriteMessage(messageType, p)
		if err != nil {
			return
		}
	}
}
```

## 4. Testing Handlers (`httptest`)

One of the most powerful features of Go is the `httptest` package. It allows you to test your web server *without actually starting the server on a port*.

It creates a fake `ResponseWriter` and a fake `Request` that you can pass directly into your handler function.

```go
package main

import (
	"net/http"
	"net/http/httptest"
	"testing"
)

// The handler we want to test
func pingHandler(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("pong"))
}

func TestPingHandler(t *testing.T) {
	// 1. Create a fake request
	req, err := http.NewRequest("GET", "/ping", nil)
	if err != nil {
		t.Fatal(err)
	}

	// 2. Create a fake ResponseWriter (the Recorder)
	rr := httptest.NewRecorder()

	// 3. Call the handler directly, passing in our fakes!
	handler := http.HandlerFunc(pingHandler)
	handler.ServeHTTP(rr, req)

	// 4. Assert the results
	if status := rr.Code; status != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v", status, http.StatusOK)
	}

	expected := "pong"
	if rr.Body.String() != expected {
		t.Errorf("handler returned unexpected body: got %v want %v", rr.Body.String(), expected)
	}
}
```

### Summary of Chapter 5
You have graduated from basic handlers to building production-ready architectures that can test themselves, handle browser security restrictions, communicate in real-time, and shut down politely.

At this point, you could build an entire massive application using nothing but the standard library. So... why do people use Frameworks?

**Let's explore that in the final chapter: [Chapter 6: Frameworks vs. Standard Library](06-FRAMEWORKS-VS-STDLIB.md)**
