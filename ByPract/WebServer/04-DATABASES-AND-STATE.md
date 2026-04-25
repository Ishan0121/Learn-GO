# Chapter 4: Databases, State & Concurrency



<div align="center">
  <audio controls src="audio/04-DATABASES-AND-STATE.wav" title="Go Learning Audio Session" style="width: 100%; max-width: 400px; margin-bottom: 20px;"></audio>
  <p><i>Listen to the audio version above!</i></p>
</div>

So far, our web server can route traffic and respond with JSON. But true applications need to store data permanently.

In Node.js or Python, handling state and database connections is relatively straightforward. But in Go, because of **concurrency** (handling many requests simultaneously on different Goroutines), handling state wrong will crash your server instantly.

## 1. The Danger of Global Variables (The Shared Notepad)

Imagine your web server is an office building. Every time a request comes in, you hire a new worker (a Goroutine) to handle it.
If two workers try to write to the exact same piece of paper (a global variable) at the exact same millisecond, the paper rips. This is called a **Race Condition** or a **Data Race**, and Go will crash your program to protect the data.

### Bad Practice ❌

```go
package main

import "net/http"

// GLOBAL STATE - DANGEROUS!
var hitCount = 0

func hitHandler(w http.ResponseWriter, r *http.Request) {
    // If 10,000 Goroutines hit this line at the same time, your server panics.
	hitCount++ 
}
```

### The Solution: Mutexes (Locks) 🔒

A Mutex (Mutual Exclusion) is like a talking stick. A worker can only write to the paper if they are holding the stick. Everyone else must wait in line.

```go
package main

import (
	"fmt"
	"net/http"
	"sync"
)

type ServerState struct {
	mu       sync.Mutex // The Lock
	hitCount int
}

func (s *ServerState) hitHandler(w http.ResponseWriter, r *http.Request) {
	s.mu.Lock()   // GRAB THE STICK!
	s.hitCount++  // Safely modify the data
	count := s.hitCount
	s.mu.Unlock() // DROP THE STICK so the next Goroutine can use it

	fmt.Fprintf(w, "You are visitor number %d", count)
}

func main() {
    // Create an instance of our state
	state := &ServerState{}
	
    // We bind the handler to our state struct!
	http.HandleFunc("/", state.hitHandler)
	http.ListenAndServe(":8080", nil)
}
```

By making our handler a *method* on a struct (`func (s *ServerState)`), we safely inject dependencies without using global variables.

## 2. Databases & Connection Pooling (The Vault)

You want to connect to a PostgreSQL, MySQL, or SQLite database. You might think:
*"I should open a database connection every time someone makes a request!"*
**NO. Do not do this.** Opening a database connection is incredibly slow. If 1,000 people request a page, you will overwhelm the database with 1,000 login attempts.

### Connection Pooling
Instead, you open a **Connection Pool** when the server boots up. The pool keeps, say, 50 connections open constantly. When a Goroutine needs to run a query, it borrows a connection from the pool, runs the query, and puts it back.

Go's `database/sql` package handles this pool *automatically* behind the scenes!

### The Perfect Database Architecture

Notice how we use the Struct pattern from earlier to safely pass the Database Pool into our handlers without making it global.

```go
package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"

	_ "github.com/mattn/go-sqlite3" // Import the driver (underscore means run its init function only)
)

// 1. Define our Server Application Struct
type Application struct {
	DB *sql.DB // The connection pool
}

// 2. Define a handler as a method on the Application
func (app *Application) getUserHandler(w http.ResponseWriter, r *http.Request) {
	userID := r.URL.Query().Get("id")

	// QueryRow asks the pool for a connection, runs the query, and returns the connection.
	var username string
	err := app.DB.QueryRow("SELECT username FROM users WHERE id = ?", userID).Scan(&username)
	
	if err == sql.ErrNoRows {
		http.Error(w, "User not found", http.StatusNotFound)
		return
	} else if err != nil {
		http.Error(w, "Server Error", http.StatusInternalServerError)
		return
	}

	fmt.Fprintf(w, "Hello, %s!", username)
}

func main() {
	// 3. Open the connection pool ONLY ONCE when booting up
	db, err := sql.Open("sqlite3", "./my_database.db")
	if err != nil {
		log.Fatal(err) // Crash if we can't build the pool
	}
	defer db.Close() // Ensure the pool closes when the server shuts down

	// 4. Ping to verify the database is actually reachable
	if err = db.Ping(); err != nil {
		log.Fatal(err)
	}

	// 5. Inject the DB into our Application struct
	app := &Application{
		DB: db,
	}

	// 6. Register routes
	http.HandleFunc("/user", app.getUserHandler)

	fmt.Println("Server running on :8080")
	http.ListenAndServe(":8080", nil)
}
```

### Summary of Chapter 4
- Never use global variables for state unless they are Read-Only.
- If you must mutate state, use `sync.Mutex` to prevent Goroutines from corrupting data.
- Never open a database connection *inside* a handler. Open it once in `main()`, and pass the connection pool to your handlers using a Struct wrapper.

You are now capable of building a fully functional, safe, database-backed API. But what about making it ready for the harsh reality of the internet?

**Let's move on to [Chapter 5: Advanced Concepts (Security, Websockets, Testing)](05-ADVANCED-CONCEPTS.md)**
