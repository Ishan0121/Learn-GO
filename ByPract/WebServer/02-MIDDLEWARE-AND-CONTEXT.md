# Chapter 2: Middlewares & Context



<div align="center">
  <audio controls src="audio/02-MIDDLEWARE-AND-CONTEXT.wav" title="Go Learning Audio Session" style="width: 100%; max-width: 400px; margin-bottom: 20px;"></audio>
  <p><i>Listen to the audio version above!</i></p>
</div>

Now that our server can route traffic and respond to users, we face a new problem: **Repetition**.

Imagine you want to:
1. Log every incoming request.
2. Check if the user is authenticated before allowing access.
3. Add security headers to every response.

You *could* write this logic inside every single handler, but that violates the DRY (Don't Repeat Yourself) principle.

## 1. What is Middleware? (The Bouncer Analogy)

Think of a nightclub. Before you reach the bartender (the **Handler**), you have to get past the bouncer (the **Middleware**).
The bouncer checks your ID.
- If you're underage (unauthorized), the bouncer kicks you out immediately. The bartender never even knows you were there.
- If you are good to go, the bouncer steps aside and lets you pass to the bartender.

In Go, a Middleware is simply a function that takes an `http.Handler`, wraps it with some extra logic, and returns a *new* `http.Handler`. This is a classic software design pattern known as the **Decorator Pattern**.

### Writing a Logging Middleware

Let's build a middleware that logs how long every request takes.

```go
package main

import (
	"log"
	"net/http"
	"time"
)

// Our middleware takes the NEXT handler in the chain
func LoggingMiddleware(next http.Handler) http.Handler {
    // It returns an anonymous handler that wraps the original logic
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// --- BEFORE THE HANDLER ---
		start := time.Now()

		// THE ACTUAL HANDLER RUNS HERE
		next.ServeHTTP(w, r)

		// --- AFTER THE HANDLER ---
		duration := time.Since(start)
		log.Printf("[%s] %s took %v", r.Method, r.URL.Path, duration)
	})
}
```

### How to Apply Middleware

To use it, you literally wrap your handler with it when registering the route:

```go
func mySecretPage(w http.ResponseWriter, r *http.Request) {
	w.Write([]byte("Super secret dashboard"))
}

func main() {
	mux := http.NewServeMux()

	// Wrap the handler!
    // Note: http.HandlerFunc(mySecretPage) converts our function into the http.Handler interface
	mux.Handle("GET /dashboard", LoggingMiddleware(http.HandlerFunc(mySecretPage)))

	http.ListenAndServe(":8080", mux)
}
```

### Chaining Multiple Middlewares
If you have Authentication, Logging, and Rate Limiting, wrapping them can look ugly:
`Auth(Logging(RateLimit(myHandler)))`.

Most developers create a helper function to chain them cleanly, or use a tiny 3rd party router just for this feature.

---

## 2. The Backpack: `context.Context`

This is arguably the most important, yet confusing, concept for Go beginners.

Imagine a user makes an HTTP request to your server. Your server then makes an HTTP request to an external database, which takes 5 seconds.
*What happens if the user gets bored after 2 seconds and closes their browser tab?*

Without `context`, your server will continue waiting for the database for another 3 seconds, wasting CPU and memory on a user who is already gone!

### What is Context?
The `context.Context` is like a **backpack** that is created the exact millisecond the request hits your server. This backpack travels with the request everywhere it goes—through middlewares, to the handler, and down into the database queries.

It is used for two main things:
1. **Cancellation / Timeouts:** If the user disconnects, the backpack sends an alert: *"Hey, abort mission! Stop everything!"*
2. **Request-Scoped Data:** You can put data inside the backpack in a middleware and pull it out in the handler.

### Accessing the Context
Every `http.Request` has the backpack built-in.

```go
ctx := r.Context()
```

### Example 1: Passing Data with Context

Let's write an Authentication middleware. It checks the token, figures out who the user is, puts their ID in the backpack, and sends them to the handler.

```go
type contextKey string
const userIDKey contextKey = "userID"

func AuthMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		token := r.Header.Get("Authorization")
        
		if token != "secret-password" {
			http.Error(w, "Unauthorized!", http.StatusUnauthorized)
			return // Kick them out!
		}

		// The user is valid. Let's pretend their ID is 42.
		// We create a NEW backpack by adding data to the old backpack.
		ctx := context.WithValue(r.Context(), userIDKey, 42)

		// Create a NEW request carrying the NEW backpack
		reqWithNewBackpack := r.WithContext(ctx)

		// Let them pass to the handler, but pass the new request!
		next.ServeHTTP(w, reqWithNewBackpack)
	})
}
```

Now, inside your actual Handler, you can open the backpack and get the user ID!

```go
func DashboardHandler(w http.ResponseWriter, r *http.Request) {
    // Open the backpack and extract the value
	userID := r.Context().Value(userIDKey)
	
	fmt.Fprintf(w, "Welcome to your dashboard, User #%v!", userID)
}
```

### Example 2: Cancellation (Handling Client Disconnects)

If a handler does heavy work (like processing a large file or doing an expensive DB query), you should constantly check the context to see if it has been cancelled.

```go
func SlowTaskHandler(w http.ResponseWriter, r *http.Request) {
	ctx := r.Context()

    // Simulate heavy work using a select statement
	select {
	case <-time.After(5 * time.Second):
		// If 5 seconds pass normally, we finish the work
		w.Write([]byte("Heavy work finished!"))
		
	case <-ctx.Done():
		// If the user closes their browser before 5 seconds, this triggers!
		err := ctx.Err()
		log.Println("Client disconnected. Aborting heavy work!", err)
		// We don't need to write to the response because the client is gone.
	}
}
```

### Summary of Chapter 2
You now understand how to intercept requests using Middleware (Decorator Pattern) and how to manage the lifecycle and data of a request using the `context.Context` backpack.

Next, we need to talk about the universal language of APIs: JSON.

**Let's move on to [Chapter 3: Data, JSON, & APIs](03-DATA-AND-JSON.md)**
