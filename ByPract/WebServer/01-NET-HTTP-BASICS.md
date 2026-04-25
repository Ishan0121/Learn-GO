# Chapter 1: The Core Mechanics of `net/http` & Go 1.22 Routing


<div align="center">
  <audio controls src="audio/01-NET-HTTP-BASICS.wav" title="Go Learning Audio Session" style="width: 100%; max-width: 400px; margin-bottom: 20px;"></audio>
  <p><i>Listen to the audio version above!</i></p>
</div>


Welcome to the Kitchen. To build a server, you need to understand the core package that powers almost all web frameworks in Go: `net/http`.

## 1. The Anatomy of a Handler

A "Handler" is the function that actually processes an incoming request and returns a response. It is the chef who cooks the specific dish.

Every standard handler in Go has this exact signature:

```go
func myHandler(w http.ResponseWriter, r *http.Request) {
    // ...
}
```

Let's break down the two arguments:

### `r *http.Request` (The Order Ticket)
This is a pointer to a struct containing *everything* the client sent you.
- `r.Method` (Is it a GET, POST, DELETE?)
- `r.URL.Path` (Are they asking for `/home` or `/users`?)
- `r.Header` (Hidden metadata, like authentication tokens or "Accept: application/json").
- `r.Body` (The payload, like the JSON data of a new user they want to create).

### `w http.ResponseWriter` (The Delivery Tray)
This is an interface used to construct the response you send *back* to the client.
You use it to:
1. Write the actual data (HTML, JSON, plain text).
2. Set the HTTP Status Code (200 OK, 404 Not Found, 500 Internal Error).
3. Set Response Headers (Telling the browser "Hey, the stuff I'm sending is JSON!").

---

## 2. Your First "Hello World" Server

Let's build the absolute minimum viable server.

```go
package main

import (
	"fmt"
	"net/http"
)

// 1. The Handler
func welcomeHandler(w http.ResponseWriter, r *http.Request) {
    // fmt.Fprintf writes formatted text directly to our ResponseWriter (the tray)
	fmt.Fprintf(w, "Welcome to the ultimate Go server!")
}

func main() {
	// 2. The Router (Mux)
	// We tell the default router: "If someone asks for the '/' path, use the welcomeHandler"
	http.HandleFunc("/", welcomeHandler)

	// 3. Start the Server
    fmt.Println("Server booting up on port 8080...")
	// ListenAndServe blocks forever, keeping the program alive to listen for traffic.
	err := http.ListenAndServe(":8080", nil)
	if err != nil {
		fmt.Println("Server crashed:", err)
	}
}
```

---

## 3. The Revolution: Go 1.22 Routing Superpowers

For years, Go's built-in router (the `ServeMux`) was extremely basic. If you wanted to extract a user ID from a URL like `/users/42` or restrict a route to only `POST` requests, you had to write messy custom code or download a framework like `Chi` or `Gorilla Mux`.

**Go 1.22 changed everything.** The standard library now supports HTTP Methods and Wildcards natively.

### Method Matching
Before 1.22, `http.HandleFunc("/users", ...)` would accept GET, POST, DELETE, everything. You had to manually check `r.Method` inside the handler. Now, you declare it in the route string:

```go
// Only accepts GET requests. A POST will automatically get a "405 Method Not Allowed"
http.HandleFunc("GET /users", listUsersHandler)

// Only accepts POST requests.
http.HandleFunc("POST /users", createUserHandler)
```

### Path Wildcards (Variables)
You can now capture dynamic parts of the URL natively!

```go
// We use {id} as a wildcard
http.HandleFunc("GET /users/{id}", func(w http.ResponseWriter, r *http.Request) {
    // We extract the value using r.PathValue()
    userID := r.PathValue("id")
    
    fmt.Fprintf(w, "You are looking for user number: %s", userID)
})
```

### Wildcard Matches All `...`
If you want to catch everything under a specific folder (like serving static images or CSS), you use the `...` syntax.

```go
// Matches /files/image.png, /files/docs/report.pdf, etc.
http.HandleFunc("GET /files/{filepath...}", func(w http.ResponseWriter, r *http.Request) {
    path := r.PathValue("filepath")
    fmt.Fprintf(w, "Looking for file: %s", path)
})
```

---

## 4. Building a Modern Go 1.22 API

Let's combine these new features into a clean, modern, standard-library-only server:

```go
package main

import (
	"fmt"
	"net/http"
)

func main() {
    // It's best practice to create your own ServeMux (Router) rather than using the global one.
	mux := http.NewServeMux()

	// 1. Exact Match
	mux.HandleFunc("GET /", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("Welcome to the homepage!"))
	})

	// 2. Fetch all items
	mux.HandleFunc("GET /posts", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("List of all posts..."))
	})

	// 3. Create an item
	mux.HandleFunc("POST /posts", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("Creating a new post..."))
	})

	// 4. Fetch a specific item using a Wildcard
	mux.HandleFunc("GET /posts/{id}", func(w http.ResponseWriter, r *http.Request) {
		id := r.PathValue("id")
		w.Write([]byte(fmt.Sprintf("Fetching post ID: %s", id)))
	})

	// 5. Delete an item
	mux.HandleFunc("DELETE /posts/{id}", func(w http.ResponseWriter, r *http.Request) {
		id := r.PathValue("id")
		w.Write([]byte(fmt.Sprintf("Deleted post ID: %s", id)))
	})

	fmt.Println("🚀 Server running on http://localhost:8080")
	http.ListenAndServe(":8080", mux)
}
```

### Summary of Chapter 1
You now know how to listen for requests, inspect the method, route traffic cleanly using Go 1.22 features, and extract dynamic data from the URL.

However, right now, our server is naked. If an error happens, it doesn't log it. If a user tries to access a private route, nothing stops them.

To solve this, we need "Bouncers".
**Let's move on to [Chapter 2: Middlewares & Context](02-MIDDLEWARE-AND-CONTEXT.md)**
